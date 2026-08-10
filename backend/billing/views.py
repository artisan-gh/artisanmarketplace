# billing/views.py
import json
import requests
import hmac
import hashlib
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Invoice, Payment, CreditNote, RecurringInvoice,
    LedgerAccount, JournalEntry, BillingConfig,
    Tax, InvoiceTag, PaymentIntent,
    PaymentAllocation, InvoiceApproval,
    InvoiceHistory, InvoiceComment, InvoiceAttachment,
    InvoiceSequence, WebhookLog,
    PurchasedItem
)
from .serializers import (
    InvoiceListSerializer, InvoiceDetailSerializer, InvoiceCreateUpdateSerializer,
    PaymentListSerializer, PaymentDetailSerializer, PaymentCreateSerializer,
    CreditNoteListSerializer, CreditNoteCreateSerializer,
    RecurringInvoiceListSerializer, RecurringInvoiceDetailSerializer,
    LedgerAccountListSerializer, LedgerAccountDetailSerializer,
    JournalEntryListSerializer, JournalEntryDetailSerializer,
    BillingConfigSerializer, TaxSerializer, InvoiceTagSerializer,
    PaymentIntentListSerializer,
    PaystackInitializeSerializer, PaystackWebhookSerializer,
    RefundSerializer, InvoiceStatusTransitionSerializer,
    InvoiceApprovalActionSerializer, PaymentAllocationCreateSerializer
)
from accounts.permissions import IsAdminOrStaff
from .services import PaymentService, InvoiceService, ApprovalWorkflow, JournalEntryService


# ─── Invoice ViewSet ─────────────────────────────────────────

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related(
        'customer', 'created_by'
    ).prefetch_related(
        'items',
        'purchased_items',
        'tags',
        'approvals',
        'history',
        'payment_allocations',
        'credit_notes'
    )
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'status', 'invoice_type', 'currency', 'customer',
        'issued_date', 'due_date', 'paid_date', 'organization'
    ]
    search_fields = ['invoice_number', 'customer__name', 'customer__email']
    ordering_fields = ['created_at', 'due_date', 'grand_total']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        if user.is_staff:
            if self.request.query_params.get('mine') == 'true':
                return qs.filter(customer__user=user)
            return qs
        else:
            return qs.filter(customer__user=user)

    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return InvoiceCreateUpdateSerializer
        return InvoiceDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminOrStaff]
        elif self.action in ['send_invoice']:  # <-- only admin can send
            self.permission_classes = [IsAdminOrStaff]
        elif self.action in ['initialize_payment']:
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['verify_payment', 'paystack_webhook', 'public_detail']:
            self.permission_classes = []
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # ─── Custom Actions ──────────────────────────────────────

    @action(detail=True, methods=['post'])
    def transition_status(self, request, pk=None):
        """
        Transition the invoice status.
        Only Admin/Staff can transition to 'SENT' status.
        """
        invoice = self.get_object()
        serializer = InvoiceStatusTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['new_status']
        reason = serializer.validated_data.get('reason', '')

        # ─── Block non‑admins from sending ──────────────────
        if new_status == 'SENT' and not request.user.is_staff:
            return Response(
                {'error': 'Only administrators can send invoices.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            invoice.transition_status(new_status, user=request.user, reason=reason)
            return Response({'status': 'transitioned', 'new_status': new_status})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='send')
    def send_invoice(self, request, pk=None):
        """
        Explicit action to send an invoice. Only Admin/Staff can call this.
        """
        invoice = self.get_object()
        if invoice.status != 'DRAFT':
            return Response(
                {'error': f'Invoice is already {invoice.status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            invoice.transition_status('SENT', user=request.user, reason='Invoice sent by admin.')
            return Response({'status': 'sent', 'invoice_number': invoice.invoice_number})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        invoice = self.get_object()
        serializer = InvoiceCommentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(invoice=invoice, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        invoice = self.get_object()
        serializer = InvoiceAttachmentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        attachment = serializer.save(invoice=invoice, uploaded_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def start_approval(self, request, pk=None):
        invoice = self.get_object()
        approval = ApprovalWorkflow.start_approval_workflow(invoice, user=request.user)
        if approval:
            return Response({'status': 'approval_started', 'level': approval.level})
        return Response({'status': 'auto_approved'})

    @action(detail=True, methods=['post'])
    def approve_level(self, request, pk=None):
        invoice = self.get_object()
        level = request.data.get('level')
        comments = request.data.get('comments', '')
        if not level:
            return Response({'error': 'level required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            ApprovalWorkflow.approve_level(invoice, level, request.user, comments)
            return Response({'status': 'approved'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def initialize_payment(self, request, pk=None):
        """
        Initialize Paystack payment for an invoice.
        """
        invoice = self.get_object()
        serializer = PaystackInitializeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if invoice.grand_total <= 0:
            return Response(
                {'error': 'Invoice amount must be greater than zero.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        customer_email = invoice.customer.email
        if not customer_email:
            return Response(
                {'error': 'Customer email is required for payment. Please update the customer record.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        paystack_secret = getattr(settings, 'PAYSTACK_SECRET_KEY', None)
        if not paystack_secret:
            return Response(
                {'error': 'Paystack secret key not configured.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        callback_url = serializer.validated_data.get('callback_url') or \
                       getattr(settings, 'PAYSTACK_CALLBACK_URL', None)
        if not callback_url:
            return Response(
                {'error': 'Callback URL not configured.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        amount = invoice.amount_in_smallest_unit
        if amount <= 0:
            return Response(
                {'error': f'Invalid amount: {amount}. Grand total: {invoice.grand_total}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        paystack_url = 'https://api.paystack.co/transaction/initialize'
        headers = {
            'Authorization': f'Bearer {paystack_secret}',
            'Content-Type': 'application/json',
        }
        payload = {
            'amount': amount,
            'email': customer_email,
            'reference': f'INV-{invoice.id.hex[:8]}-{int(timezone.now().timestamp())}',
            'callback_url': callback_url,
            'currency': invoice.currency or 'GHS',
            'metadata': {
                'invoice_id': str(invoice.id),
                'invoice_number': invoice.invoice_number,
                'customer_id': str(invoice.customer.id),
                'customer_name': invoice.customer.name,
            }
        }

        print(f"🔵 Paystack Payload: {payload}")

        try:
            resp = requests.post(paystack_url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            print(f"✅ Paystack Response: {result}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Paystack request error: {str(e)}")
            if hasattr(e, 'response') and e.response:
                print(f"Response body: {e.response.text}")
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('message', str(e))
                except:
                    error_msg = str(e)
                return Response(
                    {'error': f'Paystack error: {error_msg}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return Response(
                {'error': f'Paystack error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if not result.get('status'):
            error_msg = result.get('message', 'Paystack initialization failed.')
            print(f"❌ Paystack returned error: {error_msg}")
            return Response(
                {'error': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        invoice.paystack_reference = result['data']['reference']
        invoice.paystack_access_code = result['data']['access_code']
        invoice.status = 'SENT'
        invoice.save(update_fields=['paystack_reference', 'paystack_access_code', 'status'])

        return Response({
            'authorization_url': result['data']['authorization_url'],
            'reference': result['data']['reference'],
            'access_code': result['data']['access_code'],
            'invoice': InvoiceDetailSerializer(invoice).data
        })

    @action(detail=False, methods=['post'], url_path='webhook', permission_classes=[])
    def paystack_webhook(self, request):
        serializer = PaystackWebhookSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)

        event = serializer.validated_data['event']
        data = serializer.validated_data['data']

        paystack_secret = getattr(settings, 'PAYSTACK_SECRET_KEY', None)
        signature = request.headers.get('x-paystack-signature')
        if paystack_secret and signature:
            computed = hmac.new(
                paystack_secret.encode(),
                request.body,
                hashlib.sha512
            ).hexdigest()
            if not hmac.compare_digest(signature, computed):
                return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)

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

        if event == 'charge.success':
            reference = data.get('reference')
            if reference:
                invoice = Invoice.objects.filter(paystack_reference=reference).first()
                if invoice and invoice.status != 'PAID':
                    payment = Payment.objects.create(
                        customer=invoice.customer,
                        amount=invoice.grand_total,
                        currency=invoice.currency,
                        method='PAYSTACK',
                        gateway='PAYSTACK',
                        gateway_reference=reference,
                        status='SUCCESS',
                        paid_at=timezone.now(),
                        metadata={'webhook': data}
                    )
                    PaymentAllocation.objects.create(
                        payment=payment,
                        invoice=invoice,
                        amount=invoice.grand_total
                    )
                    invoice.update_paid_amount()
                    invoice.create_payment_journal_entry()
                    InvoiceHistory.objects.create(
                        invoice=invoice,
                        action='PAID',
                        reason='Payment received via Paystack webhook'
                    )
                    webhook_log.processed = True
                    webhook_log.status = 'PROCESSED'
                    webhook_log.save()

        return Response({'status': 'success'})

    @action(detail=False, methods=['get'], url_path='verify', permission_classes=[])
    def verify_payment(self, request):
        reference = request.query_params.get('reference')
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')

        if not reference:
            return redirect(f"{frontend_url}/payment-failed?error=Missing reference")

        # ─── Find invoice ──────────────────────────────────────────
        # 1. Try exact match by reference
        invoice = Invoice.objects.filter(paystack_reference=reference).first()

        # 2. Fallback: get metadata from Paystack and search by invoice_number
        if not invoice:
            paystack_secret = getattr(settings, 'PAYSTACK_SECRET_KEY', None)
            if paystack_secret:
                url = f"https://api.paystack.co/transaction/verify/{reference}"
                headers = {'Authorization': f'Bearer {paystack_secret}'}
                try:
                    resp = requests.get(url, headers=headers, timeout=30)
                    if resp.status_code == 200:
                        data = resp.json().get('data', {})
                        metadata = data.get('metadata', {})
                        invoice_number = metadata.get('invoice_number')
                        if invoice_number:
                            invoice = Invoice.objects.filter(invoice_number=invoice_number).first()
                            if invoice:
                                # Sync the reference for future matches
                                Invoice.objects.filter(pk=invoice.pk).update(paystack_reference=reference)
                except Exception:
                    pass

        if not invoice:
            return redirect(f"{frontend_url}/payment-failed?error=Invoice not found")

        # ─── Already paid ──────────────────────────────────────────
        if invoice.status == 'PAID':
            return redirect(
                f"{frontend_url}/payment-success"
                f"?invoice={invoice.invoice_number}"
                f"&status=paid"
                f"&token={invoice.public_token}"
            )

        # ─── Verify with Paystack ─────────────────────────────────
        paystack_secret = getattr(settings, 'PAYSTACK_SECRET_KEY', None)
        if not paystack_secret:
            return redirect(
                f"{frontend_url}/payment-failed"
                f"?error=Paystack not configured"
                f"&token={invoice.public_token}"
            )

        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {'Authorization': f'Bearer {paystack_secret}'}

        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            result = resp.json()
        except requests.exceptions.RequestException:
            return redirect(
                f"{frontend_url}/payment-failed"
                f"?error=Paystack error"
                f"&token={invoice.public_token}"
            )

        if not result.get('status'):
            return redirect(
                f"{frontend_url}/payment-failed"
                f"?error={result.get('message', 'Verification failed')}"
                f"&token={invoice.public_token}"
            )

        data = result['data']
        if data.get('status') == 'success':
            payment_exists = Payment.objects.filter(
                gateway_reference=reference,
                allocations__invoice=invoice
            ).exists()

            if not payment_exists:
                payment = Payment.objects.create(
                    customer=invoice.customer,
                    amount=invoice.grand_total,
                    currency=invoice.currency,
                    method='PAYSTACK',
                    gateway='PAYSTACK',
                    gateway_reference=reference,
                    status='SUCCESS',
                    paid_at=timezone.now(),
                    metadata={'verification': data}
                )
                PaymentAllocation.objects.create(
                    payment=payment,
                    invoice=invoice,
                    amount=invoice.grand_total
                )
                invoice.update_paid_amount()
                invoice.create_payment_journal_entry()
                InvoiceHistory.objects.create(
                    invoice=invoice,
                    action='PAID',
                    reason='Payment verified via callback'
                )

            return redirect(
                f"{frontend_url}/payment-success"
                f"?invoice={invoice.invoice_number}"
                f"&status=paid"
                f"&token={invoice.public_token}"
            )
        else:
            return redirect(
                f"{frontend_url}/payment-failed"
                f"?error=Payment not completed"
                f"&status={data.get('status')}"
                f"&token={invoice.public_token}"
            )

    @action(detail=False, methods=['get'], url_path='my')
    def my_invoices(self, request):
        invoices = self.get_queryset().filter(customer__user=request.user)
        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='overdue')
    def overdue_invoices(self, request):
        invoices = self.get_queryset().filter(status='OVERDUE')
        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='public/(?P<token>[^/.]+)', permission_classes=[])
    def public_detail(self, request, token=None):
        try:
            invoice = Invoice.objects.get(public_token=token)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = InvoiceDetailSerializer(invoice)
        return Response(serializer.data)


# ─── Payment ViewSet ─────────────────────────────────────────

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('customer')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'method', 'currency', 'customer']
    search_fields = ['gateway_reference', 'customer__name']
    ordering_fields = ['paid_at', 'created_at', 'amount']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        if self.action == 'create':
            return PaymentCreateSerializer
        if self.action == 'refund':
            return RefundSerializer
        return PaymentDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminOrStaff]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        payment = self.get_object()
        serializer = RefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data.get('amount')
        reason = serializer.validated_data.get('reason', '')
        try:
            PaymentService.refund_payment(payment, amount, reason)
            return Response({'status': 'refunded', 'refunded_amount': payment.refunded_amount})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def allocate(self, request, pk=None):
        payment = self.get_object()
        serializer = PaymentAllocationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice_id = serializer.validated_data['invoice']
        amount = serializer.validated_data['amount']
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            PaymentAllocation.objects.create(
                payment=payment,
                invoice=invoice,
                amount=amount
            )
            return Response({'status': 'allocated'})
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='my')
    def my_payments(self, request):
        payments = self.get_queryset().filter(customer__user=request.user)
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)


# ─── Credit Note ViewSet ─────────────────────────────────────

class CreditNoteViewSet(viewsets.ModelViewSet):
    queryset = CreditNote.objects.select_related('invoice', 'payment', 'created_by')
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'currency', 'invoice']
    search_fields = ['credit_number', 'reason']
    ordering_fields = ['issued_date', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return CreditNoteCreateSerializer
        return CreditNoteListSerializer


# ─── Recurring Invoice ViewSet ──────────────────────────────

class RecurringInvoiceViewSet(viewsets.ModelViewSet):
    queryset = RecurringInvoice.objects.select_related('customer', 'organization')
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'frequency', 'customer']
    search_fields = ['customer__name']
    ordering_fields = ['next_issue_date', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return RecurringInvoiceListSerializer
        return RecurringInvoiceDetailSerializer


# ─── Ledger Account ViewSet ──────────────────────────────────

class LedgerAccountViewSet(viewsets.ModelViewSet):
    queryset = LedgerAccount.objects.filter(is_active=True)
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account_type', 'is_active']
    search_fields = ['code', 'name']
    ordering_fields = ['code']
    ordering = ['code']

    def get_serializer_class(self):
        if self.action == 'list':
            return LedgerAccountListSerializer
        return LedgerAccountDetailSerializer


# ─── Journal Entry ViewSet ───────────────────────────────────

class JournalEntryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JournalEntry.objects.select_related('invoice', 'payment')
    permission_classes = [IsAdminOrStaff]
    serializer_class = JournalEntryListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['invoice']
    search_fields = ['entry_number', 'description']
    ordering_fields = ['posted_at']
    ordering = ['-posted_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return JournalEntryDetailSerializer
        return JournalEntryListSerializer


# ─── Billing Config ViewSet ──────────────────────────────────

class BillingConfigViewSet(viewsets.ModelViewSet):
    queryset = BillingConfig.objects.filter(is_active=True)
    permission_classes = [IsAdminOrStaff]
    serializer_class = BillingConfigSerializer


# ─── Tax ViewSet ─────────────────────────────────────────────

class TaxViewSet(viewsets.ModelViewSet):
    queryset = Tax.objects.filter(is_active=True)
    permission_classes = [IsAdminOrStaff]
    serializer_class = TaxSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tax_type', 'is_active']
    search_fields = ['name', 'description']


# ─── Invoice Tag ViewSet ─────────────────────────────────────

class InvoiceTagViewSet(viewsets.ModelViewSet):
    queryset = InvoiceTag.objects.all()
    permission_classes = [IsAdminOrStaff]
    serializer_class = InvoiceTagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


# ─── Payment Intent ViewSet ──────────────────────────────────

class PaymentIntentViewSet(viewsets.ModelViewSet):
    queryset = PaymentIntent.objects.select_related('customer', 'invoice')
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentIntentListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'customer']
    search_fields = ['gateway_reference']
    ordering_fields = ['expires_at', 'created_at']
    ordering = ['-created_at']
