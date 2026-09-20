"""
Client payments installer — billing patches + React screens.

Run from: backend/
React root: ../frontend/src

Writes:
    billing/paystack.py
    billing/serializers_client.py
    billing/views_client.py
    billing/urls_client.py
    ../frontend/src/api/clientBilling.js
    ../frontend/src/api/clientIncidents.js
    ../frontend/src/screens/client/PublicInvoicePage.jsx
    ../frontend/src/screens/client/InvoicesListScreen.jsx
    ../frontend/src/screens/client/InvoiceDetailScreen.jsx
    ../frontend/src/screens/client/NewRequestScreen.jsx
    ../frontend/src/screens/client/client.css

Patches:
    billing/serializers.py   + PublicInvoiceSerializer
    billing/views.py         7 fixes (imports, lookup_value_regex x2, initialize_payment,
                             public_pay action, webhook strict sig, webhook idempotency,
                             public_detail uses PublicInvoiceSerializer)
    config/settings.py       + PAYSTACK_*, FRONTEND_URL
    config/urls.py           + /api/client/invoices/
    ../frontend/src/App.jsx  + 4 client routes
"""
from pathlib import Path
from datetime import datetime
import re
import shutil

ROOT = Path(".")
REACT_SRC = Path("../frontend/src")


def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(f"  wrote   {path}")


def append_once(path, marker, content):
    p = ROOT / path
    text = p.read_text(encoding="utf-8") if p.exists() else ""
    if marker in text:
        print(f"  skip    {path}")
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip() + "\n\n" + content.strip() + "\n", encoding="utf-8")
    print(f"  updated {path}")


def backup(path):
    p = ROOT / path
    if not p.exists(): return
    name = f"{p.stem}.backup-{datetime.now():%Y%m%d-%H%M%S}{p.suffix}"
    shutil.copy2(p, p.parent / name)
    print(f"  backup  {p.parent / name}")


_backed = set()
def bkp(path):
    if path in _backed: return
    backup(path); _backed.add(path)


def find_settings():
    for c in ("config/settings.py", "settings.py", "core/settings.py"):
        if (ROOT / c).exists(): return c
    return None


def find_root_urls():
    s = find_settings()
    if not s: return None
    text = (ROOT / s).read_text(encoding="utf-8")
    m = re.search(r'ROOT_URLCONF\s*=\s*[("\']([^"\']+)', text)
    return m.group(1).replace(".", "/") + ".py" if m else None


print("\n=== Client payments installer ===\n")

# ------------------------------------------------------------------
# 1. billing/paystack.py
# ------------------------------------------------------------------
print("[1/8] billing/paystack.py")
if (ROOT / "billing/paystack.py").exists():
    bkp("billing/paystack.py")

write("billing/paystack.py", r'''
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
''')

# ------------------------------------------------------------------
# 2. billing/serializers_client.py
# ------------------------------------------------------------------
print("\n[2/8] billing/serializers_client.py")
write("billing/serializers_client.py", r'''
from rest_framework import serializers
from .models import Invoice, InvoiceItem


class InvoiceItemClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ["description", "quantity", "unit_price",
                  "discount_amount", "tax_amount", "line_total"]
        read_only_fields = fields


class InvoiceClientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ["id", "invoice_number", "status", "currency",
                  "grand_total", "amount_paid", "balance_due",
                  "issued_date", "due_date", "paid_date", "public_token"]
        read_only_fields = fields


class InvoiceClientDetailSerializer(serializers.ModelSerializer):
    items = InvoiceItemClientSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = ["id", "invoice_number", "status", "currency",
                  "subtotal", "tax_amount", "discount_amount",
                  "materials_total", "transport_cost",
                  "grand_total", "amount_paid", "balance_due",
                  "issued_date", "due_date", "paid_date",
                  "billing_name", "billing_address", "billing_phone",
                  "notes", "terms", "items", "public_token"]
        read_only_fields = fields


class PublicInvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemClientSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = Invoice
        fields = ["invoice_number", "status", "currency",
                  "subtotal", "tax_amount", "discount_amount",
                  "materials_total", "transport_cost",
                  "grand_total", "amount_paid", "balance_due",
                  "issued_date", "due_date", "paid_date",
                  "billing_name", "billing_address", "billing_phone",
                  "notes", "terms", "items", "customer_name"]
        read_only_fields = fields


class PublicInvoicePaySerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    channel = serializers.ChoiceField(
        choices=["card", "mobile_money", "bank_transfer"],
        required=False, allow_blank=True,
    )
''')

# ------------------------------------------------------------------
# 3. billing/views_client.py
# ------------------------------------------------------------------
print("\n[3/8] billing/views_client.py")
write("billing/views_client.py", r'''
"""Client-facing + public invoice endpoints."""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Invoice
from .paystack import initialize_payment as paystack_init, PaystackError
from .serializers_client import (
    InvoiceClientDetailSerializer,
    InvoiceClientListSerializer,
    PublicInvoicePaySerializer,
    PublicInvoiceSerializer,
)


class IsClient(permissions.BasePermission):
    message = "Only client accounts can use this endpoint."

    def has_permission(self, request, view):
        u = request.user
        return (u and u.is_authenticated
                and (getattr(u, "user_type", "") or "").upper() == "CLIENT")


def _pay_response(invoice, request):
    if invoice.status in ("PAID", "CANCELLED", "VOID"):
        return Response({"detail": f"Invoice is {invoice.status.lower()}."},
                        status=status.HTTP_400_BAD_REQUEST)
    ser = PublicInvoicePaySerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    try:
        result = paystack_init(
            invoice,
            customer_email=ser.validated_data.get("email") or None,
            channel=ser.validated_data.get("channel") or None,
        )
    except PaystackError as e:
        return Response({"detail": e.message},
                        status=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR)
    if invoice.status == "DRAFT":
        invoice.status = "SENT"
        invoice.save(update_fields=["status", "updated_at"])
    return Response(result, status=status.HTTP_200_OK)


class ClientInvoiceViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    permission_classes = [IsClient]
    lookup_field = "id"

    def get_queryset(self):
        u = self.request.user
        customer = getattr(u, "customer", None)
        if not customer: return Invoice.objects.none()
        return (Invoice.objects.filter(customer=customer)
                .exclude(status__in=["CANCELLED", "VOID"])
                .select_related("customer").order_by("-created_at"))

    def get_serializer_class(self):
        if self.action == "list": return InvoiceClientListSerializer
        return InvoiceClientDetailSerializer

    @action(detail=True, methods=["post"], url_path="pay")
    def pay(self, request, id=None):
        return _pay_response(self.get_object(), request)


class PublicInvoiceView(APIView):
    permission_classes = [permissions.AllowAny]

    def _get(self, token):
        return get_object_or_404(
            Invoice.objects.select_related("customer"),
            public_token=token, is_deleted=False,
        )

    def get(self, request, token):
        invoice = self._get(token)
        if invoice.status == "SENT":
            Invoice.all_objects.filter(pk=invoice.pk).update(
                last_viewed_at=timezone.now(), status="VIEWED")
            invoice.refresh_from_db()
        return Response(PublicInvoiceSerializer(invoice).data)


class PublicInvoicePayView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, token):
        invoice = get_object_or_404(
            Invoice.objects.select_related("customer"),
            public_token=token, is_deleted=False,
        )
        return _pay_response(invoice, request)
''')

# ------------------------------------------------------------------
# 4. billing/urls_client.py
# ------------------------------------------------------------------
print("\n[4/8] billing/urls_client.py")
write("billing/urls_client.py", r'''
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views_client import (
    ClientInvoiceViewSet,
    PublicInvoicePayView,
    PublicInvoiceView,
)

app_name = "billing_client"

router = DefaultRouter()
router.register(r"", ClientInvoiceViewSet, basename="client-invoice")

urlpatterns = [
    path("public/<str:token>/pay/", PublicInvoicePayView.as_view(), name="public-invoice-pay"),
    path("public/<str:token>/", PublicInvoiceView.as_view(), name="public-invoice"),
    *router.urls,
]
''')

# ------------------------------------------------------------------
# 5. Patch billing/serializers.py
# ------------------------------------------------------------------
print("\n[5/8] billing/serializers.py")
p = ROOT / "billing/serializers.py"
if p.exists():
    text = p.read_text(encoding="utf-8")
    if "class PublicInvoiceSerializer" not in text:
        bkp("billing/serializers.py")
        text = text.rstrip() + r'''


# ============================================================
# PUBLIC INVOICE
# ============================================================

class PublicInvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = Invoice
        fields = ["invoice_number", "status", "currency",
                  "subtotal", "tax_amount", "discount_amount",
                  "materials_total", "transport_cost",
                  "grand_total", "amount_paid", "balance_due",
                  "issued_date", "due_date", "paid_date",
                  "billing_name", "billing_address", "billing_phone",
                  "notes", "terms", "items", "customer_name"]
        read_only_fields = fields
'''
        p.write_text(text, encoding="utf-8")
        print("  updated billing/serializers.py")
    else:
        print("  skip    billing/serializers.py")

# ------------------------------------------------------------------
# 6. Patch billing/views.py — the 7 fixes
# ------------------------------------------------------------------
print("\n[6/8] billing/views.py")
p = ROOT / "billing/views.py"
if p.exists():
    text = p.read_text(encoding="utf-8")
    mod = False

    # 6a. imports
    if "from django.db import transaction" not in text:
        text = text.replace("from django.conf import settings",
                            "from django.conf import settings\nfrom django.db import transaction", 1)
        mod = True; print("  + import transaction")

    if "from .paystack import" not in text:
        text = text.replace(
            "from accounts.permissions import IsAdminOrStaff",
            "from accounts.permissions import IsAdminOrStaff\n"
            "from .paystack import initialize_payment as paystack_init, PaystackError", 1)
        mod = True; print("  + import paystack wrapper")

    if "PublicInvoiceSerializer" not in text.split("from .serializers import")[1].split(")")[0]:
        text = text.replace(
            "    InvoiceApprovalActionSerializer, PaymentAllocationCreateSerializer",
            "    InvoiceApprovalActionSerializer, PaymentAllocationCreateSerializer,\n"
            "    PublicInvoiceSerializer", 1)
        mod = True; print("  + import PublicInvoiceSerializer")

    # 6b. lookup_value_regex
    if text.count("lookup_value_regex") < 2:
        text = text.replace(
            "    ordering = ['-created_at']\n\n    def get_queryset(self):\n        user = self.request.user",
            "    ordering = ['-created_at']\n"
            "    lookup_value_regex = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'\n\n"
            "    def get_queryset(self):\n        user = self.request.user", 1)
        text = text.replace(
            "    ordering = ['-created_at']\n\n    def get_serializer_class(self):\n        if self.action == 'list':\n            return PaymentListSerializer",
            "    ordering = ['-created_at']\n"
            "    lookup_value_regex = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'\n\n"
            "    def get_serializer_class(self):\n        if self.action == 'list':\n            return PaymentListSerializer", 1)
        mod = True; print("  + lookup_value_regex on Invoice + Payment viewsets")

    # 6c. Replace initialize_payment body
    if "result = paystack_init(invoice)" not in text:
        marker_start = "        customer_email = invoice.customer.email"
        end_marker = "'invoice': InvoiceDetailSerializer(invoice).data\n        })"
        if marker_start in text and end_marker in text:
            idx_start = text.index(marker_start)
            idx_end = text.index(end_marker, idx_start) + len(end_marker)
            new_init = """        try:
            result = paystack_init(invoice)
        except PaystackError as e:
            return Response(
                {'error': e.message},
                status=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if invoice.status == 'DRAFT':
            invoice.status = 'SENT'
            invoice.save(update_fields=['status', 'updated_at'])

        return Response({
            'authorization_url': result['authorization_url'],
            'reference': result['reference'],
            'access_code': result['access_code'],
            'invoice': InvoiceDetailSerializer(invoice).data,
        })"""
            text = text[:idx_start] + new_init + text[idx_end:]
            mod = True; print("  + initialize_payment uses paystack wrapper")

    # 6d. public_pay action
    if "def public_pay" not in text:
        block = '''    @action(detail=False, methods=['post'],
            url_path='public/(?P<token>[^/.]+)/pay',
            permission_classes=[])
    def public_pay(self, request, token=None):
        try:
            invoice = Invoice.objects.select_related('customer').get(
                public_token=token, is_deleted=False,
            )
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'},
                            status=status.HTTP_404_NOT_FOUND)
        if invoice.status in ('PAID', 'CANCELLED', 'VOID'):
            return Response({'error': f'Invoice is {invoice.status.lower()}.'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            result = paystack_init(invoice)
        except PaystackError as e:
            return Response({'error': e.message},
                            status=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR)
        if invoice.status == 'DRAFT':
            invoice.status = 'SENT'
            invoice.save(update_fields=['status', 'updated_at'])
        return Response({
            'authorization_url': result['authorization_url'],
            'reference': result['reference'],
            'access_code': result['access_code'],
        })

    @action(detail=False, methods=['post'], url_path='webhook', permission_classes=[])'''
        text = text.replace(
            "    @action(detail=False, methods=['post'], url_path='webhook', permission_classes=[])",
            block, 1)
        mod = True; print("  + public_pay action")

    # 6e. webhook strict signature
    old_sig = """        paystack_secret = getattr(settings, 'PAYSTACK_SECRET_KEY', None)
        signature = request.headers.get('x-paystack-signature')
        if paystack_secret and signature:
            computed = hmac.new(
                paystack_secret.encode(),
                request.body,
                hashlib.sha512
            ).hexdigest()
            if not hmac.compare_digest(signature, computed):
                return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)"""
    new_sig = """        paystack_secret = getattr(settings, 'PAYSTACK_SECRET_KEY', None)
        signature = request.headers.get('x-paystack-signature')
        if not paystack_secret:
            return Response({'error': 'Webhook not configured'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not signature:
            return Response({'error': 'Missing signature'},
                            status=status.HTTP_401_UNAUTHORIZED)
        computed = hmac.new(paystack_secret.encode(), request.body, hashlib.sha512).hexdigest()
        if not hmac.compare_digest(signature, computed):
            return Response({'error': 'Invalid signature'},
                            status=status.HTTP_401_UNAUTHORIZED)"""
    if old_sig in text:
        text = text.replace(old_sig, new_sig, 1)
        mod = True; print("  + webhook strict signature")

    # 6f. webhook idempotency + row lock
    old_charge = """        if event == 'charge.success':
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
                    webhook_log.save()"""
    new_charge = """        if event == 'charge.success':
            reference = data.get('reference')
            if reference:
                with transaction.atomic():
                    invoice = (Invoice.objects.select_for_update()
                               .filter(paystack_reference=reference).first())
                    if not invoice:
                        webhook_log.status = 'IGNORED'
                        webhook_log.error_message = f'No invoice with ref {reference}'
                        webhook_log.save(update_fields=['status', 'error_message'])
                        return Response({'status': 'ignored'})
                    if Payment.objects.filter(gateway_reference=reference).exists():
                        webhook_log.processed = True
                        webhook_log.status = 'ALREADY_PROCESSED'
                        webhook_log.save(update_fields=['processed', 'status'])
                        return Response({'status': 'already_processed'})
                    if invoice.status != 'PAID':
                        payment = Payment.objects.create(
                            customer=invoice.customer,
                            amount=invoice.grand_total,
                            currency=invoice.currency,
                            method='PAYSTACK',
                            gateway='PAYSTACK',
                            gateway_reference=reference,
                            status='SUCCESS',
                            paid_at=timezone.now(),
                            metadata={'webhook': data},
                        )
                        PaymentAllocation.objects.create(
                            payment=payment, invoice=invoice,
                            amount=invoice.grand_total)
                        invoice.update_paid_amount()
                        invoice.create_payment_journal_entry()
                        InvoiceHistory.objects.create(
                            invoice=invoice, action='PAID',
                            reason='Payment received via Paystack webhook')
                    webhook_log.processed = True
                    webhook_log.status = 'PROCESSED'
                    webhook_log.save(update_fields=['processed', 'status'])"""
    if old_charge in text:
        text = text.replace(old_charge, new_charge, 1)
        mod = True; print("  + webhook row-lock + idempotency")

    # 6g. public_detail uses PublicInvoiceSerializer
    if ("serializer = InvoiceDetailSerializer(invoice)\n        return Response(serializer.data)" in text
            and "PublicInvoiceSerializer" in text):
        text = text.replace(
            """        serializer = InvoiceDetailSerializer(invoice)
        return Response(serializer.data)""",
            """        return Response(PublicInvoiceSerializer(invoice).data)""", 1)
        mod = True; print("  + public_detail uses PublicInvoiceSerializer")

    if mod:
        bkp("billing/views.py")
        p.write_text(text, encoding="utf-8")
    else:
        print("  skip    billing/views.py")

# ------------------------------------------------------------------
# 7. Settings + urls
# ------------------------------------------------------------------
print("\n[7/8] settings + urls")

s = find_settings()
if s:
    append_once(s, "# === CLIENT PAYMENTS ===", r'''
# === CLIENT PAYMENTS ===
import os as _os
PAYSTACK_SECRET_KEY = _os.environ.get("PAYSTACK_SECRET_KEY", "")
PAYSTACK_PUBLIC_KEY = _os.environ.get("PAYSTACK_PUBLIC_KEY", "")
PAYSTACK_CALLBACK_URL = _os.environ.get(
    "PAYSTACK_CALLBACK_URL",
    "http://127.0.0.1:8000/api/billing/invoices/verify/",
)
FRONTEND_URL = _os.environ.get("FRONTEND_URL", "http://localhost:5173")
# === /CLIENT PAYMENTS ===
''')

u = find_root_urls()
if u and (ROOT / u).exists():
    p = ROOT / u
    text = p.read_text(encoding="utf-8")
    if "billing.urls_client" not in text:
        if ("from django.urls import" in text
                and "include" not in text.split("from django.urls import")[1].split("\n")[0]):
            text = text.replace("from django.urls import", "from django.urls import include,", 1)
        line = '    path("api/client/invoices/", include("billing.urls_client", namespace="billing_client")),\n'
        for needle in ("\n]", "\r\n]", "\n]\n"):
            if needle in text:
                text = text.replace(needle, line + needle, 1); break
        bkp(u); p.write_text(text, encoding="utf-8")
        print(f"  updated {u}")

# ------------------------------------------------------------------
# 8. React — API + screens + css
# ------------------------------------------------------------------
print("\n[8/8] React — client screens")

write(f"{REACT_SRC}/api/clientBilling.js", r'''
import api from './client';

export const listMyInvoices = () => api.get('/client/invoices/').then(r => r.data);
export const getMyInvoice = (id) => api.get(`/client/invoices/${id}/`).then(r => r.data);
export const payMyInvoice = (id, payload = {}) =>
  api.post(`/client/invoices/${id}/pay/`, payload).then(r => r.data);
export const getPublicInvoice = (token) =>
  api.get(`/client/invoices/public/${token}/`).then(r => r.data);
export const payPublicInvoice = (token, payload = {}) =>
  api.post(`/client/invoices/public/${token}/pay/`, payload).then(r => r.data);
''')

write(f"{REACT_SRC}/api/clientIncidents.js", r'''
import api from './client';

export const listMyIncidents = () => api.get('/client/incidents/').then(r => r.data);
export const getMyIncident = (id) => api.get(`/client/incidents/${id}/`).then(r => r.data);
export const createMyIncident = (payload) =>
  api.post('/client/incidents/', payload).then(r => r.data);
export const getMyCustomerProfile = () => api.get('/customers/me/').then(r => r.data);
''')

write(f"{REACT_SRC}/screens/client/PublicInvoicePage.jsx", r'''
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  FaFileInvoiceDollar, FaCircleNotch, FaCheckCircle,
  FaExclamationTriangle, FaLock,
} from 'react-icons/fa';
import { getPublicInvoice, payPublicInvoice } from '../../api/clientBilling';
import './client.css';

const fmt = (n, c = 'GHS') => `${c} ${Number(n || 0).toFixed(2)}`;

export default function PublicInvoicePage() {
  const { token } = useParams();
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [paying, setPaying] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await getPublicInvoice(token);
        if (!cancelled) setInvoice(data);
      } catch (e) {
        if (!cancelled) setError(e?.response?.data?.detail || 'Invoice not found.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [token]);

  const handlePay = async () => {
    setPaying(true); setError('');
    try {
      const res = await payPublicInvoice(token);
      if (res?.authorization_url) window.location.href = res.authorization_url;
      else setError('Could not initialize payment.');
    } catch (e) {
      setError(e?.response?.data?.detail || 'Payment initialization failed.');
    } finally { setPaying(false); }
  };

  if (loading) return (
    <div className="cp-page cp-page--center">
      <FaCircleNotch className="cp-spin" /><p>Loading invoice…</p>
    </div>
  );

  if (error && !invoice) return (
    <div className="cp-page cp-page--center">
      <div className="cp-alert cp-alert--error">
        <FaExclamationTriangle />
        <div><strong>Invoice unavailable</strong><p>{error}</p></div>
      </div>
    </div>
  );

  const isPaid = invoice.status === 'PAID';
  const isCancelled = ['CANCELLED', 'VOID'].includes(invoice.status);

  return (
    <div className="cp-page">
      <div className="cp-shell">
        <header className="cp-hero">
          <div className="cp-hero__icon"><FaFileInvoiceDollar /></div>
          <div>
            <span className="cp-eyebrow">Invoice</span>
            <h1>{invoice.invoice_number}</h1>
            <p>{invoice.customer_name || 'Thank you for your business'}</p>
          </div>
        </header>

        {isPaid && (
          <div className="cp-banner cp-banner--success">
            <FaCheckCircle />
            <div><strong>Payment received</strong><p>This invoice has been paid in full.</p></div>
          </div>
        )}
        {isCancelled && (
          <div className="cp-banner cp-banner--warn">
            <FaExclamationTriangle />
            <div><strong>Invoice {invoice.status.toLowerCase()}</strong>
              <p>Contact the business if you believe this is a mistake.</p></div>
          </div>
        )}

        <section className="cp-card">
          <h3>Line items</h3>
          <ul className="cp-items">
            {(invoice.items || []).map((item, i) => (
              <li key={i} className="cp-item">
                <div>
                  <strong>{item.description}</strong>
                  <span>{item.quantity} × {fmt(item.unit_price, invoice.currency)}</span>
                </div>
                <span>{fmt(item.line_total, invoice.currency)}</span>
              </li>
            ))}
            {(!invoice.items || invoice.items.length === 0) && (
              <li className="cp-item cp-item--empty">No line items</li>
            )}
          </ul>
          <div className="cp-totals">
            <div><span>Subtotal</span><strong>{fmt(invoice.subtotal, invoice.currency)}</strong></div>
            {Number(invoice.tax_amount) > 0 && (
              <div><span>Tax</span><strong>{fmt(invoice.tax_amount, invoice.currency)}</strong></div>
            )}
            {Number(invoice.transport_cost) > 0 && (
              <div><span>Transport</span><strong>{fmt(invoice.transport_cost, invoice.currency)}</strong></div>
            )}
            {Number(invoice.discount_amount) > 0 && (
              <div><span>Discount</span><strong>− {fmt(invoice.discount_amount, invoice.currency)}</strong></div>
            )}
            <div className="cp-totals__grand">
              <span>Total</span><strong>{fmt(invoice.grand_total, invoice.currency)}</strong>
            </div>
            <div className="cp-totals__due">
              <span>Amount due</span><strong>{fmt(invoice.balance_due, invoice.currency)}</strong>
            </div>
          </div>
        </section>

        {!isPaid && !isCancelled && (
          <div className="cp-pay">
            <div className="cp-pay__secure">
              <FaLock /> Secure payment via Paystack · Card or Mobile Money
            </div>
            <button type="button" className="cp-btn cp-btn--primary cp-btn--block"
                    onClick={handlePay}
                    disabled={paying || Number(invoice.balance_due) <= 0}>
              {paying
                ? <><FaCircleNotch className="cp-spin" /> Opening checkout…</>
                : <>Pay {fmt(invoice.balance_due, invoice.currency)}</>}
            </button>
            {error && <p className="cp-error">{error}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
''')

write(f"{REACT_SRC}/screens/client/InvoicesListScreen.jsx", r'''
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { FaFileInvoiceDollar, FaCircleNotch } from 'react-icons/fa';
import { listMyInvoices } from '../../api/clientBilling';
import './client.css';

const fmt = (n, c = 'GHS') => `${c} ${Number(n || 0).toFixed(2)}`;
const STATUS_LABELS = { DRAFT: 'Draft', SENT: 'Unpaid', VIEWED: 'Unpaid',
  PARTIALLY_PAID: 'Partial', PAID: 'Paid', OVERDUE: 'Overdue' };

export default function InvoicesListScreen() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['myInvoices'], queryFn: listMyInvoices,
  });
  const invoices = data?.results || data || [];

  if (isLoading) return (
    <div className="cp-page cp-page--center"><FaCircleNotch className="cp-spin" /></div>
  );
  if (error) return (
    <div className="cp-page cp-page--center"><p className="cp-error">Could not load invoices.</p></div>
  );

  return (
    <div className="cp-page">
      <div className="cp-shell">
        <header className="cp-hero">
          <div className="cp-hero__icon"><FaFileInvoiceDollar /></div>
          <div>
            <span className="cp-eyebrow">Billing</span>
            <h1>My invoices</h1>
            <p>{invoices.length} invoice{invoices.length === 1 ? '' : 's'}</p>
          </div>
        </header>

        {invoices.length === 0 ? (
          <div className="cp-empty">
            <FaFileInvoiceDollar className="cp-empty__icon" />
            <p>You have no invoices yet.</p>
          </div>
        ) : (
          <ul className="cp-list">
            {invoices.map((inv) => {
              const isPaid = inv.status === 'PAID';
              return (
                <li key={inv.id} className="cp-list-row">
                  <div className="cp-list-row__main">
                    <Link to={`/client/invoices/${inv.id}`} className="cp-list-row__ref">
                      {inv.invoice_number}
                    </Link>
                    <span className={`cp-status cp-status--${(inv.status || '').toLowerCase()}`}>
                      {STATUS_LABELS[inv.status] || inv.status}
                    </span>
                    <div className="cp-list-row__meta">
                      <span>Issued {new Date(inv.issued_date).toLocaleDateString()}</span>
                      {inv.due_date && !isPaid && (
                        <span>· Due {new Date(inv.due_date).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                  <div className="cp-list-row__amount">
                    <strong>{fmt(inv.grand_total, inv.currency)}</strong>
                    {!isPaid && Number(inv.balance_due) > 0 && (
                      <span className="cp-list-row__due">Due {fmt(inv.balance_due, inv.currency)}</span>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
''')

write(f"{REACT_SRC}/screens/client/InvoiceDetailScreen.jsx", r'''
import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { FaFileInvoiceDollar, FaCircleNotch, FaCheckCircle, FaArrowLeft, FaLock } from 'react-icons/fa';
import { getMyInvoice, payMyInvoice } from '../../api/clientBilling';
import './client.css';

const fmt = (n, c = 'GHS') => `${c} ${Number(n || 0).toFixed(2)}`;

export default function InvoiceDetailScreen() {
  const { id } = useParams();
  const [paying, setPaying] = useState(false);
  const [error, setError] = useState('');
  const { data: invoice, isLoading, error: loadErr } = useQuery({
    queryKey: ['myInvoice', id], queryFn: () => getMyInvoice(id),
  });

  const handlePay = async () => {
    setPaying(true); setError('');
    try {
      const res = await payMyInvoice(id);
      if (res?.authorization_url) window.location.href = res.authorization_url;
    } catch (e) {
      setError(e?.response?.data?.detail || 'Payment initialization failed.');
    } finally { setPaying(false); }
  };

  if (isLoading) return <div className="cp-page cp-page--center"><FaCircleNotch className="cp-spin" /></div>;
  if (loadErr || !invoice) return <div className="cp-page cp-page--center"><p className="cp-error">Invoice not found.</p></div>;

  const isPaid = invoice.status === 'PAID';
  return (
    <div className="cp-page">
      <div className="cp-shell">
        <Link to="/client/invoices" className="cp-back"><FaArrowLeft /> Back</Link>
        <header className="cp-hero">
          <div className="cp-hero__icon"><FaFileInvoiceDollar /></div>
          <div>
            <span className="cp-eyebrow">Invoice</span>
            <h1>{invoice.invoice_number}</h1>
            <p>{isPaid ? 'Paid in full' : 'Awaiting payment'}</p>
          </div>
        </header>

        {isPaid && (
          <div className="cp-banner cp-banner--success">
            <FaCheckCircle />
            <div><strong>Paid</strong><p>Thank you for your payment.</p></div>
          </div>
        )}

        <section className="cp-card">
          <h3>Line items</h3>
          <ul className="cp-items">
            {(invoice.items || []).map((item, i) => (
              <li key={i} className="cp-item">
                <div>
                  <strong>{item.description}</strong>
                  <span>{item.quantity} × {fmt(item.unit_price, invoice.currency)}</span>
                </div>
                <span>{fmt(item.line_total, invoice.currency)}</span>
              </li>
            ))}
          </ul>
          <div className="cp-totals">
            <div><span>Subtotal</span><strong>{fmt(invoice.subtotal, invoice.currency)}</strong></div>
            <div className="cp-totals__grand">
              <span>Total</span><strong>{fmt(invoice.grand_total, invoice.currency)}</strong>
            </div>
            <div className="cp-totals__due">
              <span>Amount due</span><strong>{fmt(invoice.balance_due, invoice.currency)}</strong>
            </div>
          </div>
        </section>

        {!isPaid && (
          <div className="cp-pay">
            <div className="cp-pay__secure">
              <FaLock /> Secure payment via Paystack
            </div>
            <button type="button" className="cp-btn cp-btn--primary cp-btn--block"
                    onClick={handlePay}
                    disabled={paying || Number(invoice.balance_due) <= 0}>
              {paying
                ? <><FaCircleNotch className="cp-spin" /> Opening checkout…</>
                : <>Pay {fmt(invoice.balance_due, invoice.currency)}</>}
            </button>
            {error && <p className="cp-error">{error}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
''')

write(f"{REACT_SRC}/screens/client/NewRequestScreen.jsx", r'''
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { FaCircleNotch, FaMapMarkerAlt, FaCamera } from 'react-icons/fa';
import { createMyIncident } from '../../api/clientIncidents';
import './client.css';

const PRIORITIES = [
  { value: 'URGENT', label: 'As soon as possible' },
  { value: 'HIGH', label: 'Today' },
  { value: 'MEDIUM', label: 'This week' },
  { value: 'LOW', label: 'Whenever possible' },
];

export default function NewRequestScreen() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ title: '', description: '', priority: 'MEDIUM', address: '' });
  const [error, setError] = useState('');

  const mutation = useMutation({
    mutationFn: createMyIncident,
    onSuccess: (data) => navigate(`/client/requests/${data.id}`),
    onError: (e) => setError(e?.response?.data?.detail || 'Could not create request.'),
  });

  const handleChange = (e) => {
    setForm((p) => ({ ...p, [e.target.name]: e.target.value }));
    setError('');
  };

  const handleUseLocation = () => {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        setForm((p) => ({ ...p, address: `${p.address ? p.address + ' · ' : ''}${latitude.toFixed(5)}, ${longitude.toFixed(5)}` }));
      },
      () => setError('Could not access your location.'),
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.title.trim()) { setError('Please tell us what you need help with.'); return; }
    mutation.mutate(form);
  };

  return (
    <div className="cp-page">
      <div className="cp-shell">
        <header className="cp-hero">
          <div className="cp-hero__icon"><FaCamera /></div>
          <div>
            <span className="cp-eyebrow">New request</span>
            <h1>How can we help?</h1>
            <p>Tell us what you need and we'll send the right artisan.</p>
          </div>
        </header>

        <form onSubmit={handleSubmit} className="cp-form">
          <div className="cp-field">
            <label htmlFor="title">What's the issue? *</label>
            <input id="title" name="title" value={form.title} onChange={handleChange}
                   placeholder="e.g. Kitchen socket sparks when I plug in the kettle"
                   className={error && !form.title.trim() ? 'has-error' : ''} />
          </div>

          <div className="cp-field">
            <label htmlFor="description">More details</label>
            <textarea id="description" name="description" value={form.description}
                      onChange={handleChange} rows={4}
                      placeholder="Anything else we should know?" />
          </div>

          <div className="cp-field">
            <label>When do you need it?</label>
            <div className="cp-chips">
              {PRIORITIES.map((p) => (
                <button key={p.value} type="button"
                        className={`cp-chip ${form.priority === p.value ? 'is-active' : ''}`}
                        onClick={() => setForm((prev) => ({ ...prev, priority: p.value }))}>
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          <div className="cp-field">
            <label htmlFor="address">Where is it happening?</label>
            <div className="cp-input-group">
              <FaMapMarkerAlt />
              <input id="address" name="address" value={form.address}
                     onChange={handleChange} placeholder="Address or GPS coordinates" />
              <button type="button" className="cp-btn cp-btn--ghost cp-btn--sm"
                      onClick={handleUseLocation}>Use my location</button>
            </div>
          </div>

          {error && <p className="cp-error">{error}</p>}

          <button type="submit" className="cp-btn cp-btn--primary cp-btn--block"
                  disabled={mutation.isLoading}>
            {mutation.isLoading
              ? <><FaCircleNotch className="cp-spin" /> Sending request…</>
              : 'Request a service'}
          </button>
        </form>
      </div>
    </div>
  );
}
''')

write(f"{REACT_SRC}/screens/client/client.css", r'''
:root {
  color-scheme: light;
  --cp-bg: #f2f4fb; --cp-ink-900: #0b1226; --cp-ink-700: #334155;
  --cp-ink-500: #64748b; --cp-ink-300: #cbd5e1; --cp-line: #e8ecf5;
  --cp-blue: #0a35d6; --cp-blue-soft: #eef1fb;
  --cp-green: #10b981; --cp-green-soft: #eaf6f2;
  --cp-amber: #f59e0b; --cp-amber-soft: #fef3e2;
  --cp-red: #ef4444; --cp-red-soft: #fef2f2;
  --cp-radius: 18px;
  --cp-font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
.cp-page {
  min-height: 100vh; padding: 20px 16px 32px;
  background: radial-gradient(900px 500px at 10% -10%, rgba(10,53,214,0.06), transparent 60%),
              linear-gradient(180deg, #f7f8fc 0%, #eef1f9 100%);
  font-family: var(--cp-font); color: var(--cp-ink-900);
  max-width: 640px; margin: 0 auto;
}
.cp-page--center {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 12px; min-height: 60vh; color: var(--cp-ink-500);
}
.cp-shell { display: flex; flex-direction: column; gap: 16px; }
.cp-hero { display: flex; align-items: flex-start; gap: 14px; padding: 4px 0 8px; }
.cp-hero__icon {
  flex-shrink: 0; width: 48px; height: 48px; border-radius: 14px;
  display: grid; place-items: center;
  background: linear-gradient(135deg, #0a35d6, #1a4dff); color: #fff; font-size: 20px;
  box-shadow: 0 14px 28px -14px rgba(10,53,214,0.6);
}
.cp-eyebrow {
  display: inline-block; font-size: 10.5px; font-weight: 800;
  letter-spacing: 1.2px; text-transform: uppercase;
  color: var(--cp-blue); background: var(--cp-blue-soft);
  padding: 4px 10px; border-radius: 999px; margin-bottom: 6px;
}
.cp-hero h1 { margin: 0 0 2px; font-size: 24px; font-weight: 800; letter-spacing: -0.7px; }
.cp-hero p { margin: 0; font-size: 13.5px; color: var(--cp-ink-500); }
.cp-back {
  display: inline-flex; align-items: center; gap: 6px; font-size: 13px;
  font-weight: 600; color: var(--cp-blue); text-decoration: none; margin-bottom: 4px;
}
.cp-card {
  padding: 20px; background: #fff; border: 1px solid var(--cp-line);
  border-radius: var(--cp-radius); box-shadow: 0 2px 10px -4px rgba(15,23,42,0.08);
}
.cp-card h3 { margin: 0 0 14px; font-size: 15px; font-weight: 800; }
.cp-items { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; }
.cp-item {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--cp-line); font-size: 13.5px;
}
.cp-item:last-child { border-bottom: 0; }
.cp-item > div { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.cp-item strong { font-weight: 700; }
.cp-item span { font-size: 12px; color: var(--cp-ink-500); }
.cp-item--empty { justify-content: center; color: var(--cp-ink-500); font-style: italic; }
.cp-totals {
  margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--cp-line);
  display: flex; flex-direction: column; gap: 8px; font-size: 13.5px;
}
.cp-totals > div { display: flex; justify-content: space-between; }
.cp-totals span { color: var(--cp-ink-500); }
.cp-totals strong { font-variant-numeric: tabular-nums; }
.cp-totals__grand {
  padding: 10px 0; border-top: 1px dashed var(--cp-line);
  border-bottom: 1px dashed var(--cp-line); font-size: 15px;
}
.cp-totals__grand span { color: var(--cp-ink-900); font-weight: 700; }
.cp-totals__grand strong { font-size: 18px; font-weight: 800; }
.cp-totals__due strong { color: var(--cp-blue); font-size: 16px; font-weight: 800; }

.cp-banner {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 14px 16px; border-radius: var(--cp-radius); font-size: 13.5px; line-height: 1.5;
}
.cp-banner > svg { font-size: 20px; flex-shrink: 0; margin-top: 2px; }
.cp-banner strong { display: block; font-weight: 800; margin-bottom: 2px; }
.cp-banner p { margin: 0; opacity: 0.9; }
.cp-banner--success { background: var(--cp-green-soft); color: #065f46; border: 1px solid #a7f3d0; }
.cp-banner--success svg { color: var(--cp-green); }
.cp-banner--warn { background: var(--cp-amber-soft); color: #92400e; border: 1px solid #fde68a; }
.cp-banner--warn svg { color: var(--cp-amber); }

.cp-alert {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 16px 18px; border-radius: var(--cp-radius); font-size: 13.5px;
}
.cp-alert--error { background: var(--cp-red-soft); color: #991b1b; border: 1px solid #fecaca; }
.cp-alert svg { font-size: 20px; flex-shrink: 0; margin-top: 2px; }
.cp-alert strong { display: block; font-weight: 800; margin-bottom: 2px; }
.cp-alert p { margin: 0; }

.cp-pay {
  display: flex; flex-direction: column; gap: 12px;
  padding: 18px; background: #fff; border: 1px solid var(--cp-line);
  border-radius: var(--cp-radius); box-shadow: 0 2px 10px -4px rgba(15,23,42,0.08);
}
.cp-pay__secure {
  display: inline-flex; align-items: center; gap: 8px; font-size: 11.5px;
  font-weight: 600; color: var(--cp-ink-500); letter-spacing: 0.3px;
}
.cp-pay__secure svg { color: var(--cp-green); }

.cp-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  padding: 14px 20px; font: inherit; font-size: 14px; font-weight: 700;
  border-radius: 14px; border: 1.5px solid transparent; cursor: pointer;
  transition: all 0.2s ease; text-decoration: none;
}
.cp-btn--primary {
  background: linear-gradient(135deg, #0a35d6, #1a4dff); color: #fff;
  box-shadow: 0 14px 28px -14px rgba(10,53,214,0.75);
}
.cp-btn--primary:hover:not(:disabled) { transform: translateY(-1px); }
.cp-btn--primary:disabled { opacity: 0.6; cursor: not-allowed; }
.cp-btn--ghost { background: #fff; border-color: var(--cp-line); color: var(--cp-ink-700); }
.cp-btn--ghost:hover { border-color: var(--cp-blue); color: var(--cp-blue); }
.cp-btn--sm { padding: 9px 14px; font-size: 12.5px; }
.cp-btn--block { width: 100%; }

.cp-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; }
.cp-list-row {
  display: flex; align-items: center; justify-content: space-between;
  gap: 14px; padding: 16px 18px; background: #fff;
  border: 1.5px solid var(--cp-line); border-radius: var(--cp-radius);
  transition: all 0.2s ease;
}
.cp-list-row:hover {
  border-color: rgba(10,53,214,0.35);
  box-shadow: 0 12px 26px -16px rgba(10,53,214,0.35); transform: translateY(-2px);
}
.cp-list-row__main { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.cp-list-row__ref {
  font-size: 13.5px; font-weight: 800; color: var(--cp-blue);
  text-decoration: none; padding: 3px 9px; border-radius: 8px; background: var(--cp-blue-soft);
}
.cp-list-row__meta {
  display: flex; flex-wrap: wrap; gap: 6px; font-size: 12px;
  color: var(--cp-ink-500); margin-top: 4px; width: 100%;
}
.cp-list-row__amount { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; }
.cp-list-row__amount strong { font-size: 15px; font-weight: 800; font-variant-numeric: tabular-nums; }
.cp-list-row__due { font-size: 11.5px; color: var(--cp-blue); font-weight: 700; }

.cp-status {
  display: inline-flex; padding: 4px 10px; border-radius: 999px;
  font-size: 10.5px; font-weight: 800; letter-spacing: 0.6px; text-transform: uppercase;
  background: #f1f4f9; color: var(--cp-ink-700);
}
.cp-status--paid { background: var(--cp-green-soft); color: #06795f; }
.cp-status--overdue { background: var(--cp-red-soft); color: #991b1b; }
.cp-status--partially_paid { background: var(--cp-amber-soft); color: #92400e; }
.cp-status--sent, .cp-status--viewed { background: var(--cp-blue-soft); color: var(--cp-blue); }

.cp-empty {
  display: flex; flex-direction: column; align-items: center;
  gap: 10px; padding: 48px 24px; text-align: center;
  border-radius: var(--cp-radius); background: #fff;
  border: 1px dashed var(--cp-line); color: var(--cp-ink-500);
}
.cp-empty__icon { font-size: 32px; color: var(--cp-ink-300); }
.cp-empty p { margin: 0; }

.cp-form { display: flex; flex-direction: column; gap: 16px; }
.cp-field { display: flex; flex-direction: column; gap: 6px; }
.cp-field label { font-size: 12.5px; font-weight: 700; color: var(--cp-ink-700); }
.cp-field input, .cp-field textarea {
  font: inherit; font-size: 14.5px; padding: 13px 16px;
  border-radius: 14px; border: 1.5px solid var(--cp-line);
  background: #fff; color: var(--cp-ink-900);
  transition: border-color 0.2s ease, box-shadow 0.2s ease; outline: none; width: 100%;
}
.cp-field input:focus, .cp-field textarea:focus {
  border-color: var(--cp-blue); box-shadow: 0 0 0 4px rgba(10,53,214,0.12);
}
.cp-field input.has-error { border-color: var(--cp-red); }
.cp-field textarea { resize: vertical; min-height: 96px; }

.cp-input-group {
  display: flex; align-items: center; gap: 8px; padding-left: 14px;
  background: #fff; border: 1.5px solid var(--cp-line); border-radius: 14px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.cp-input-group:focus-within {
  border-color: var(--cp-blue); box-shadow: 0 0 0 4px rgba(10,53,214,0.12);
}
.cp-input-group > svg { color: var(--cp-ink-500); flex-shrink: 0; }
.cp-input-group input { flex: 1; border: 0; padding: 13px 8px; background: transparent; }
.cp-input-group input:focus { box-shadow: none; }
.cp-input-group .cp-btn { margin-right: 6px; }

.cp-chips { display: flex; gap: 8px; flex-wrap: wrap; }
.cp-chip {
  padding: 9px 14px; font: inherit; font-size: 13px; font-weight: 700;
  border-radius: 999px; border: 1.5px solid var(--cp-line);
  background: #fff; color: var(--cp-ink-700); cursor: pointer; transition: all 0.2s ease;
}
.cp-chip:hover { border-color: var(--cp-blue); color: var(--cp-blue); }
.cp-chip.is-active {
  background: linear-gradient(135deg, #0a35d6, #1a4dff); color: #fff;
  border-color: transparent; box-shadow: 0 8px 18px -8px rgba(10,53,214,0.6);
}
.cp-error { margin: 0; font-size: 13px; font-weight: 600; color: var(--cp-red); }
.cp-spin { animation: cp-spin 0.9s linear infinite; }
@keyframes cp-spin { to { transform: rotate(360deg); } }

@media (min-width: 640px) { .cp-page { padding: 32px 24px 48px; } }
''')

# Patch App.jsx for client routes
app = None
for c in (f"{REACT_SRC}/App.jsx", f"{REACT_SRC}/App.tsx", f"{REACT_SRC}/routes.jsx"):
    if (ROOT / c).exists(): app = c; break

if app:
    p = ROOT / app
    text = p.read_text(encoding="utf-8")
    if "/client/invoices" not in text:
        imports = '''import PublicInvoicePage from './screens/client/PublicInvoicePage';
import InvoicesListScreen from './screens/client/InvoicesListScreen';
import InvoiceDetailScreen from './screens/client/InvoiceDetailScreen';
import NewRequestScreen from './screens/client/NewRequestScreen';
'''
        lines = text.split("\n")
        last_import = 0
        for i, l in enumerate(lines):
            if l.startswith("import "): last_import = i
        lines.insert(last_import + 1, imports.rstrip())
        text = "\n".join(lines)

        routes = '''
          {/* ─── Client (self-service) ─────────────────────── */}
          <Route path="/client/invoices" element={<InvoicesListScreen />} />
          <Route path="/client/invoices/:id" element={<InvoiceDetailScreen />} />
          <Route path="/client/requests/new" element={<NewRequestScreen />} />
          <Route path="/pay/:token" element={<PublicInvoicePage />} />
'''
        for marker in ('{/* ─── Catch-all', '<Route path="*" element=', '<Route path="*"'):
            if marker in text:
                idx = text.index(marker)
                text = text[:idx] + routes + "\n          " + text[idx:]
                break
        bkp(app); p.write_text(text, encoding="utf-8")
        print(f"  updated {app}")
    else:
        print(f"  skip    {app}")

print("\n=== Done ===\n")
print("""
Next steps:

1. Ensure .env has:
       PAYSTACK_SECRET_KEY=sk_test_...
       PAYSTACK_PUBLIC_KEY=pk_test_...
       PAYSTACK_CALLBACK_URL=http://127.0.0.1:8000/api/billing/invoices/verify/
       FRONTEND_URL=http://localhost:5173

2. Restart Django + Vite.

3. Test the flow:
       http://localhost:5173/login-phone       → enter phone → OTP → in
       http://localhost:5173/client/invoices   → list of invoices
       http://localhost:5173/client/invoices/<id>  → detail + pay
       http://localhost:5173/client/requests/new   → new request
       http://localhost:5173/pay/<token>          → public SMS-link pay page
""")