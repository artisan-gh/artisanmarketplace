# billing/utils.py
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .paystack import initialize_payment

logger = logging.getLogger(__name__)


def send_invoice_email(invoice, recipient_email):
    """
    Generate a Paystack payment link and send an invoice email.
    The invoice object must have all related fields (items, purchased_items, etc.)
    available, as the template uses them to render line items and materials.
    """
    payment_url = None
    reference = None

    # ---------------------------------------------------------
    # Initialize Paystack payment
    # ---------------------------------------------------------
    try:
        logger.info(
            "Initializing Paystack payment for invoice %s",
            invoice.invoice_number,
        )

        payment_url, reference = initialize_payment(
            invoice=invoice,
            customer_email=recipient_email,
            amount=invoice.grand_total,
        )

        logger.info("Payment URL generated successfully.")
        logger.info("Reference: %s", reference)
        logger.info("URL: %s", payment_url)

        # Save reference and payment link if the fields exist on the model
        fields_to_update = []

        if hasattr(invoice, "payment_link"):
            invoice.payment_link = payment_url
            fields_to_update.append("payment_link")

        if hasattr(invoice, "payment_reference"):
            invoice.payment_reference = reference
            fields_to_update.append("payment_reference")

        if hasattr(invoice, "paystack_reference"):
            invoice.paystack_reference = reference
            fields_to_update.append("paystack_reference")

        if fields_to_update:
            invoice.save(update_fields=fields_to_update)

    except Exception:
        logger.exception(
            "Failed to initialize Paystack payment for invoice %s",
            invoice.invoice_number,
        )
        payment_url = None

    # ---------------------------------------------------------
    # Email context
    # ---------------------------------------------------------
    context = {
        "invoice": invoice,
        "customer": invoice.customer,
        "payment_link": payment_url,
        "site_url": getattr(
            settings,
            "FRONTEND_URL",
            "http://localhost:5173",
        ),
        "support_email": settings.DEFAULT_FROM_EMAIL,
    }

    # ---------------------------------------------------------
    # Render templates – the HTML template now includes:
    #   - Line items (invoice.items.all)
    #   - Materials (invoice.purchased_items.all)
    #   - Subtotal, tax, discount, materials total, grand total
    # ---------------------------------------------------------
    html_message = render_to_string(
        "billing/email/invoice_email.html",
        context,
    )

    plain_message = strip_tags(html_message)

    # ---------------------------------------------------------
    # Send email
    # ---------------------------------------------------------
    try:
        send_mail(
            subject=f"Invoice #{invoice.invoice_number} – ArtisanHub",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(
            "Invoice email successfully sent to %s",
            recipient_email,
        )

        return True

    except Exception:
        logger.exception(
            "Failed to send invoice email to %s",
            recipient_email,
        )
        return False