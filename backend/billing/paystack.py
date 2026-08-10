import requests
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

PAYSTACK_BASE_URL = "https://api.paystack.co"


def initialize_payment(invoice, customer_email, amount):
    url = f"{PAYSTACK_BASE_URL}/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    amount_pesewas = int(float(amount) * 100)

    reference = f"INV-{invoice.invoice_number}-{int(timezone.now().timestamp())}"

    payload = {
        "email": customer_email,
        "amount": amount_pesewas,
        "reference": reference,
        "callback_url": settings.PAYSTACK_CALLBACK_URL,
        "currency": invoice.currency or "GHS",
        "metadata": {
            "invoice_id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
        },
    }

    logger.info("PAYSTACK REQUEST")
    logger.info(payload)

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=30,
    )

    logger.info("STATUS: %s", response.status_code)
    logger.info("BODY: %s", response.text)

    response.raise_for_status()

    result = response.json()

    if not result.get("status"):
        raise Exception(result.get("message"))

    return (
        result["data"]["authorization_url"],
        result["data"]["reference"],
    )