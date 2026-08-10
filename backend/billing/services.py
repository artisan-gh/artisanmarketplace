"""
Billing Services – encapsulates business logic for invoices, payments, credit notes, journal entries, and Paystack.
"""
from decimal import Decimal, ROUND_HALF_UP
import requests
import hmac
import hashlib
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import (
    Invoice, InvoiceItem, InvoiceItemTax, CreditNote,
    Payment, PaymentAllocation, JournalEntry, JournalEntryLine,
    LedgerAccount, InvoiceHistory, InvoiceApproval, Tax, BillingConfig,
    PaymentIntent, WebhookLog
)


class CreditNoteService:
    """Handles creation and management of credit notes."""

    @staticmethod
    def create_from_refund(payment, amount, reason=""):
        """
        Create a credit note for a refund.
        """
        if not payment.invoice:
            raise ValueError("Payment must be linked to an invoice to create a credit note.")

        credit_note = CreditNote.objects.create(
            invoice=payment.invoice,
            payment=payment,
            amount=amount,
            reason=reason or f"Refund for payment {payment.gateway_reference}",
            currency=payment.currency,
            created_by=getattr(payment, 'created_by', None),
            issued_date=timezone.now().date()
        )
        # Update invoice balance
        credit_note.invoice.calculate_totals()
        credit_note.invoice.save_totals()
        return credit_note

    @staticmethod
    def create_from_invoice(invoice, amount, reason=""):
        """
        Create a credit note for an invoice without a payment.
        """
        credit_note = CreditNote.objects.create(
            invoice=invoice,
            payment=None,
            amount=amount,
            reason=reason or f"Credit note for invoice {invoice.invoice_number}",
            currency=invoice.currency,
            created_by=None,
            issued_date=timezone.now().date()
        )
        invoice.calculate_totals()
        invoice.save_totals()
        return credit_note


class JournalEntryService:
    """Handles creation of journal entries for accounting."""

    @staticmethod
    def create_entry(invoice, description, lines):
        """
        Create a journal entry with the given lines.
        lines is a list of dicts: {'account': account_obj, 'debit': Decimal, 'credit': Decimal, 'description': str}
        """
        with transaction.atomic():
            entry = JournalEntry.objects.create(
                description=description,
                invoice=invoice,
                posted_at=timezone.now()
            )
            for line_data in lines:
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=line_data['account'],
                    debit=line_data.get('debit', Decimal("0")),
                    credit=line_data.get('credit', Decimal("0")),
                    description=line_data.get('description', '')
                )
            return entry

    @staticmethod
    def create_invoice_approval_entry(invoice):
        """
        Create journal entry for invoice approval:
        Dr Accounts Receivable
        Cr Revenue
        """
        ar_account = LedgerAccount.objects.filter(
            account_type='ASSET',
            organization=invoice.organization,
            is_active=True
        ).first()
        revenue_account = LedgerAccount.objects.filter(
            account_type='REVENUE',
            organization=invoice.organization,
            is_active=True
        ).first()
        if not ar_account or not revenue_account:
            return None
        return JournalEntryService.create_entry(
            invoice=invoice,
            description=f"Invoice {invoice.invoice_number} approved",
            lines=[
                {'account': ar_account, 'debit': invoice.grand_total, 'description': f"Invoice {invoice.invoice_number} - AR"},
                {'account': revenue_account, 'credit': invoice.grand_total, 'description': f"Invoice {invoice.invoice_number} - Revenue"}
            ]
        )

    @staticmethod
    def create_payment_entry(invoice, amount):
        """
        Create journal entry for payment received:
        Dr Cash/Bank
        Cr Accounts Receivable
        """
        cash_account = LedgerAccount.objects.filter(
            account_type='ASSET',
            organization=invoice.organization,
            is_active=True
        ).exclude(name__icontains='receivable').first()
        ar_account = LedgerAccount.objects.filter(
            account_type='ASSET',
            organization=invoice.organization,
            is_active=True
        ).first()
        if not cash_account or not ar_account:
            return None
        return JournalEntryService.create_entry(
            invoice=invoice,
            description=f"Payment received for invoice {invoice.invoice_number}",
            lines=[
                {'account': cash_account, 'debit': amount, 'description': f"Invoice {invoice.invoice_number} - Cash"},
                {'account': ar_account, 'credit': amount, 'description': f"Invoice {invoice.invoice_number} - AR"}
            ]
        )

    @staticmethod
    def create_refund_entry(invoice, amount):
        """
        Create journal entry for refund:
        Dr Refund Expense
        Cr Cash/Bank
        """
        refund_account = LedgerAccount.objects.filter(
            account_type='EXPENSE',
            organization=invoice.organization,
            is_active=True
        ).first()
        cash_account = LedgerAccount.objects.filter(
            account_type='ASSET',
            organization=invoice.organization,
            is_active=True
        ).exclude(name__icontains='receivable').first()
        if not refund_account or not cash_account:
            return None
        return JournalEntryService.create_entry(
            invoice=invoice,
            description=f"Refund for invoice {invoice.invoice_number}",
            lines=[
                {'account': refund_account, 'debit': amount, 'description': f"Invoice {invoice.invoice_number} - Refund"},
                {'account': cash_account, 'credit': amount, 'description': f"Invoice {invoice.invoice_number} - Cash"}
            ]
        )


class InvoiceService:
    """Handles invoice-related business logic."""

    @staticmethod
    def apply_late_fee(invoice):
        """
        Apply late fee if applicable.
        """
        invoice.apply_late_fee()

    @staticmethod
    def approve_invoice(invoice, user):
        """
        Approve an invoice (full workflow) – triggers journal entry via transition_status.
        """
        invoice.transition_status('APPROVED', user=user)
        # Journal entry is automatically created in transition_status

    @staticmethod
    def send_invoice(invoice, user=None):
        """
        Mark invoice as sent and log email.
        """
        invoice.transition_status('SENT', user=user)


class PaymentService:
    """Handles payment processing and refunds."""

    @staticmethod
    def process_payment(payment, allocations):
        """
        Process a payment by creating allocations.
        allocations: list of {'invoice_id': uuid, 'amount': Decimal}
        """
        with transaction.atomic():
            total_allocated = sum(a['amount'] for a in allocations)
            if total_allocated > payment.amount:
                raise ValidationError("Total allocations exceed payment amount.")

            for alloc_data in allocations:
                invoice = Invoice.objects.get(id=alloc_data['invoice_id'])
                PaymentAllocation.objects.create(
                    payment=payment,
                    invoice=invoice,
                    amount=alloc_data['amount']
                )
                # Update invoice paid amount
                invoice.update_paid_amount()

            payment.status = 'SUCCESS'
            payment.paid_at = timezone.now()
            payment.save(update_fields=['status', 'paid_at'])

            # Trigger journal entry for each invoice
            for alloc_data in allocations:
                invoice = Invoice.objects.get(id=alloc_data['invoice_id'])
                JournalEntryService.create_payment_entry(invoice, alloc_data['amount'])

            return payment

    @staticmethod
    def refund_payment(payment, amount=None, reason=""):
        """
        Process a refund using the Payment model's refund method.
        """
        if not payment.is_successful:
            raise ValidationError("Only successful payments can be refunded.")
        refund_amount = amount or payment.amount
        if refund_amount <= 0:
            raise ValidationError("Refund amount must be positive.")
        if refund_amount > payment.refund_balance:
            raise ValidationError(f"Refund amount exceeds remaining balance of {payment.refund_balance}.")

        # Use the Payment's built-in refund method
        payment.refund(refund_amount, reason)
        return payment


class TaxCalculator:
    """Handles tax calculations."""

    @staticmethod
    def calculate_item_taxes(item):
        """
        Calculate tax for an invoice item.
        """
        from .models import InvoiceItemTax
        total_tax = Decimal("0")
        for item_tax in item.item_taxes.select_related('tax').all():
            rate = item_tax.rate_override or item_tax.tax.rate
            tax_amount = (item.line_subtotal * rate / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            item_tax.amount = tax_amount
            item_tax.save(update_fields=['amount'])
            total_tax += tax_amount
        item.tax_amount = total_tax
        item.tax_rate = total_tax / item.line_subtotal * Decimal("100") if item.line_subtotal > 0 else Decimal("0")
        item.save(update_fields=['tax_amount', 'tax_rate'])
        return total_tax


class ApprovalWorkflow:
    """Manages invoice approval workflow."""

    @staticmethod
    def get_next_approval_level(invoice):
        """
        Determine the next approval level based on invoice amount.
        """
        amount = invoice.grand_total
        if amount < 500:
            return None  # auto-approve
        elif amount < 5000:
            return 'MANAGER'
        elif amount < 50000:
            return 'FINANCE'
        else:
            return 'DIRECTOR'

    @staticmethod
    def start_approval_workflow(invoice, user=None):
        """
        Start the approval workflow for an invoice.
        """
        level = ApprovalWorkflow.get_next_approval_level(invoice)
        if not level:
            # Auto-approve
            invoice.transition_status('APPROVED', user=user)
            return None

        invoice.transition_status('PENDING_APPROVAL', user=user)
        approval = InvoiceApproval.objects.create(
            invoice=invoice,
            level=level,
            approver=user,
            status='PENDING'
        )
        return approval

    @staticmethod
    def approve_level(invoice, level, approver, comments=None):
        """
        Mark a specific approval level as approved.
        """
        approval = InvoiceApproval.objects.get(invoice=invoice, level=level)
        approval.status = 'APPROVED'
        approval.approved_at = timezone.now()
        approval.comments = comments or ''
        approval.save()

        # Check if all approvals are done
        if all(a.status == 'APPROVED' for a in invoice.approvals.all()):
            invoice.mark_approved(approver)
            # Journal entry is automatically created in transition_status

        return approval


# ─── Paystack Service ─────────────────────────────────────────

class PaystackService:
    """Handles Paystack API interactions."""

    @staticmethod
    def initialize_transaction(invoice, callback_url=None):
        """
        Initialize a Paystack transaction for an invoice.
        Returns the authorization_url and reference.
        """
        paystack_secret = getattr(settings, 'PAYSTACK_SECRET_KEY', None)
        if not paystack_secret:
            raise ValueError("PAYSTACK_SECRET_KEY not configured.")

        if not callback_url:
            callback_url = getattr(settings, 'PAYSTACK_CALLBACK_URL', None)
        if not callback_url:
            raise ValueError("PAYSTACK_CALLBACK_URL not configured.")

        paystack_url = 'https://api.paystack.co/transaction/initialize'
        headers = {
            'Authorization': f'Bearer {paystack_secret}',
            'Content-Type': 'application/json',
        }
        payload = {
            'amount': invoice.amount_in_smallest_unit,
            'email': invoice.customer.email or 'customer@example.com',
            'reference': f'{invoice.invoice_number}-{timezone.now().timestamp()}',
            'callback_url': callback_url,
            'currency': invoice.currency,
            'metadata': {
                'invoice_id': str(invoice.id),
                'invoice_number': invoice.invoice_number,
                'customer_id': str(invoice.customer.id),
                'customer_name': invoice.customer.name,
            }
        }

        try:
            resp = requests.post(paystack_url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            result = resp.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f'Paystack error: {str(e)}')

        if not result.get('status'):
            raise Exception(result.get('message', 'Paystack initialization failed.'))

        # Save the reference on the invoice
        invoice.paystack_reference = result['data']['reference']
        invoice.paystack_access_code = result['data']['access_code']
        invoice.status = 'SENT'
        invoice.save(update_fields=['paystack_reference', 'paystack_access_code', 'status'])

        return {
            'authorization_url': result['data']['authorization_url'],
            'reference': result['data']['reference'],
            'access_code': result['data']['access_code'],
        }

    @staticmethod
    def verify_transaction(reference):
        """
        Verify a Paystack transaction.
        Returns the verification result.
        """
        paystack_secret = getattr(settings, 'PAYSTACK_SECRET_KEY', None)
        if not paystack_secret:
            raise ValueError("PAYSTACK_SECRET_KEY not configured.")

        verify_url = f'https://api.paystack.co/transaction/verify/{reference}'
        headers = {'Authorization': f'Bearer {paystack_secret}'}

        try:
            resp = requests.get(verify_url, headers=headers, timeout=30)
            resp.raise_for_status()
            result = resp.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f'Paystack error: {str(e)}')

        if not result.get('status'):
            raise Exception(result.get('message', 'Verification failed.'))

        return result['data']

    @staticmethod
    def handle_webhook(request):
        """
        Handle Paystack webhook payload.
        Returns the event and data.
        """
        # Verify signature
        paystack_secret = getattr(settings, 'PAYSTACK_SECRET_KEY', None)
        signature = request.headers.get('x-paystack-signature')
        if paystack_secret and signature:
            computed = hmac.new(
                paystack_secret.encode(),
                request.body,
                hashlib.sha512
            ).hexdigest()
            if not hmac.compare_digest(signature, computed):
                raise ValidationError("Invalid signature")

        # Log webhook
        webhook_log = WebhookLog.objects.create(
            gateway='PAYSTACK',
            headers=dict(request.headers),
            payload=request.data,
            signature=signature or '',
            verified=bool(signature and paystack_secret),
            processed=False,
            retry_count=0,
            status='RECEIVED'
        )

        data = request.data
        event = data.get('event')
        event_data = data.get('data', {})

        if event == 'charge.success':
            reference = event_data.get('reference')
            if reference:
                invoice = Invoice.objects.filter(paystack_reference=reference).first()
                if invoice and invoice.status != 'PAID':
                    # Create payment
                    payment = Payment.objects.create(
                        customer=invoice.customer,
                        amount=invoice.grand_total,
                        currency=invoice.currency,
                        method='PAYSTACK',
                        gateway='PAYSTACK',
                        gateway_reference=reference,
                        status='SUCCESS',
                        paid_at=timezone.now(),
                        metadata={'webhook': event_data}
                    )
                    # Allocate payment
                    PaymentAllocation.objects.create(
                        payment=payment,
                        invoice=invoice,
                        amount=invoice.grand_total
                    )
                    invoice.update_paid_amount()
                    InvoiceHistory.objects.create(
                        invoice=invoice,
                        action='PAID',
                        reason='Payment received via Paystack webhook'
                    )
                    # Update webhook log
                    webhook_log.processed = True
                    webhook_log.status = 'PROCESSED'
                    webhook_log.save()

        return {'event': event, 'data': event_data}