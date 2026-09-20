
"""Paystack wrapper for billing."""
import logging
import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)
PAYSTACK_BASE_URL = "https://api.paystack.co"


class PaystackError(Exception):
    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}


def _headers():
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def initialize_payment(invoice, customer_email=None, amount=None, channel=None):
    if not settings.PAYSTACK_SECRET_KEY:
        raise PaystackError("PAYSTACK_SECRET_KEY is not configured.")
    if not getattr(settings, "PAYSTACK_CALLBACK_URL", None):
        raise PaystackError("PAYSTACK_CALLBACK_URL is not configured.")

    if amount is None:
        amount = invoice.balance_due or invoice.grand_total
    if amount is None or float(amount) <= 0:
        raise PaystackError("Amount must be greater than zero.")

    amount_pesewas = int(round(float(amount) * 100))

    reference = invoice.paystack_reference or (
        f"INV-{invoice.invoice_number}-{int(timezone.now().timestamp())}"
    )

    if not customer_email:
        customer_email = (
            getattr(invoice.customer, "email", None)
            or getattr(getattr(invoice.customer, "user", None), "email", None)
            or invoice.billing_email
            or f"invoice-{invoice.id.hex[:8]}@noreply.tumakonect.local"
        )

    payload = {
        "email": customer_email,
        "amount": amount_pesewas,
        "reference": reference,
        "callback_url": settings.PAYSTACK_CALLBACK_URL,
        "currency": invoice.currency or "GHS",
        "metadata": {
            "invoice_id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
            "customer_id": str(invoice.customer_id),
        },
    }
    if channel:
        payload["channels"] = [channel]

    logger.info("Paystack init → ref=%s amount=%s", reference, amount_pesewas)

    try:
        response = requests.post(
            f"{PAYSTACK_BASE_URL}/transaction/initialize",
            json=payload, headers=_headers(), timeout=30,
        )
    except requests.RequestException as e:
        logger.exception("Paystack network error: %s", e)
        _log_attempt(invoice, reference, payload, {}, "FAILED", str(e))
        raise PaystackError(f"Paystack network error: {e}")

    if response.status_code >= 400:
        try: body = response.json()
        except ValueError: body = {"raw": response.text}
        message = body.get("message", "Paystack rejected the request.")
        _log_attempt(invoice, reference, payload, body, "FAILED", message)
        raise PaystackError(message, status_code=response.status_code, payload=body)

    result = response.json()
    if not result.get("status"):
        message = result.get("message", "Paystack initialization failed.")
        _log_attempt(invoice, reference, payload, result, "FAILED", message)
        raise PaystackError(message, payload=result)

    data = result["data"]
    invoice.paystack_reference = data["reference"]
    invoice.paystack_access_code = data.get("access_code", "")
    invoice.save(update_fields=["paystack_reference", "paystack_access_code", "updated_at"])
    _log_attempt(invoice, data["reference"], payload, data, "INITIATED")

    return {
        "authorization_url": data["authorization_url"],
        "reference": data["reference"],
        "access_code": data.get("access_code"),
        "raw": data,
    }


def verify_transaction(reference):
    if not settings.PAYSTACK_SECRET_KEY:
        raise PaystackError("PAYSTACK_SECRET_KEY is not configured.")
    try:
        response = requests.get(
            f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}",
            headers=_headers(), timeout=30,
        )
    except requests.RequestException as e:
        raise PaystackError(f"Paystack network error: {e}")

    if response.status_code >= 400:
        try: body = response.json()
        except ValueError: body = {"raw": response.text}
        raise PaystackError(body.get("message", "Verify failed."),
                            status_code=response.status_code, payload=body)
    result = response.json()
    if not result.get("status"):
        raise PaystackError(result.get("message", "Verify failed."))
    return result["data"]


def _log_attempt(invoice, reference, request_payload, response_payload,
                 status_value, error_message=""):
    try:
        from .models import PaymentGatewayTransaction
        PaymentGatewayTransaction.objects.create(
            gateway="PAYSTACK", reference=reference,
            payload=request_payload, response=response_payload,
            status=status_value, verified=False,
        )
    except Exception as e:
        logger.warning("Could not log PaymentGatewayTransaction: %s", e)
