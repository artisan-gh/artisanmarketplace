"""
Client identity installer — Customer schema + OTP auth + React screens.

Run from: backend/ (where manage.py lives)
React root: ../frontend/src

Writes:
    accounts/otp.py
    accounts/sms.py
    accounts/serializers_otp.py
    accounts/views_otp.py
    accounts/client_urls.py
    accounts/management/__init__.py
    accounts/management/commands/__init__.py
    accounts/management/commands/send_test_sms.py
    customers/serializers.py          (full rewrite)
    customers/views.py                (full rewrite)
    customers/admin.py                (full rewrite)
    customers/templates/admin/customers/link_user_form.html
    ../frontend/src/api/authClient.js
    ../frontend/src/screens/auth/PhoneEntryScreen.jsx
    ../frontend/src/screens/auth/OtpVerifyScreen.jsx
    ../frontend/src/screens/auth/auth.css

Patches:
    accounts/models.py        + phone, OTPCode
    accounts/admin.py         + OTPCode admin
    customers/models.py       + user OneToOne, unique phone
    config/settings.py        + OTP + SMS + CACHE
    config/urls.py            + /api/auth/
    ../frontend/src/App.jsx   + /login-phone, /login-otp routes
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
    if not p.exists():
        return
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


# ==================================================================
print("\n=== Client identity installer ===\n")

# ------------------------------------------------------------------
# 1. accounts/models.py
# ------------------------------------------------------------------
print("[1/12] accounts/models.py")

p = ROOT / "accounts/models.py"
if p.exists():
    text = p.read_text(encoding="utf-8")
    mod = False

    if "phone = models.CharField" not in text:
        m = re.search(r"(\n\s+user_type\s*=\s*models\.CharField\([^)]+\)\n)", text)
        if m:
            phone = (
                '\n    phone = models.CharField(\n'
                '        max_length=20, unique=True, null=True, blank=True,\n'
                '        db_index=True,\n'
                '        help_text="Required for CLIENT users. Optional for staff.",\n'
                '    )\n'
            )
            text = text[:m.end(1)] + phone + text[m.end(1):]
            mod = True
            print("  + User.phone")
    if mod:
        bkp("accounts/models.py")
        p.write_text(text, encoding="utf-8")

    append_once("accounts/models.py", "# === OTP_CODE_MODEL ===", r'''
# === OTP_CODE_MODEL ===
class OTPCode(models.Model):
    PURPOSE = [("login", "Login"), ("verify", "Verify phone")]
    phone = models.CharField(max_length=20, db_index=True)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=16, choices=PURPOSE, default="login")
    attempts = models.PositiveSmallIntegerField(default=0)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone", "created_at"]),
            models.Index(fields=["phone", "used_at"]),
        ]
    def __str__(self):
        return f"{self.phone} · {self.code} · used={bool(self.used_at)}"
# === /OTP_CODE_MODEL ===
''')
else:
    print("  !!      accounts/models.py missing")

# ------------------------------------------------------------------
# 2. accounts/otp.py
# ------------------------------------------------------------------
print("\n[2/12] accounts/otp.py")
write("accounts/otp.py", r'''
"""OTP issue + verify + rate limits."""
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from .models import OTPCode

OTP_TTL = getattr(settings, "OTP_TTL_SECONDS", 300)
OTP_MAX_ATTEMPTS = getattr(settings, "OTP_MAX_ATTEMPTS", 3)
OTP_MAX_PER_HOUR = getattr(settings, "OTP_MAX_PER_HOUR", 5)
OTP_MAX_PER_HOUR_PER_IP = getattr(settings, "OTP_MAX_PER_HOUR_PER_IP", 20)


def _rate_key_phone(phone): return f"otp:rate:phone:{phone}"
def _rate_key_ip(ip): return f"otp:rate:ip:{ip}" if ip else None


def _check_rate_limit(phone, ip):
    if cache.get(_rate_key_phone(phone), 0) >= OTP_MAX_PER_HOUR:
        raise ValueError("Too many codes requested for this number. Try again later.")
    ip_key = _rate_key_ip(ip)
    if ip_key and cache.get(ip_key, 0) >= OTP_MAX_PER_HOUR_PER_IP:
        raise ValueError("Too many requests. Try again later.")
    return _rate_key_phone(phone), ip_key


def _bump(phone_key, ip_key):
    for key in (phone_key, ip_key):
        if not key: continue
        try: cache.incr(key)
        except ValueError: cache.set(key, 1, timeout=3600)


@transaction.atomic
def issue_otp(phone, ip=None, purpose="login"):
    phone = (phone or "").strip()
    if not phone:
        raise ValueError("Phone is required.")
    phone_key, ip_key = _check_rate_limit(phone, ip)
    OTPCode.objects.filter(phone=phone, used_at__isnull=True).update(used_at=timezone.now())
    code = f"{secrets.randbelow(1_000_000):06d}"
    OTPCode.objects.create(phone=phone, code=code, purpose=purpose, ip_address=ip)
    _bump(phone_key, ip_key)
    return code


@transaction.atomic
def verify_otp(phone, code, purpose="login"):
    phone = (phone or "").strip()
    code = (code or "").strip()
    otp = (OTPCode.objects.select_for_update()
           .filter(phone=phone, purpose=purpose)
           .order_by("-created_at").first())
    if not otp: return False, "no_code"
    if otp.used_at: return False, "already_used"
    if timezone.now() - otp.created_at > timedelta(seconds=OTP_TTL):
        return False, "expired"
    if otp.attempts >= OTP_MAX_ATTEMPTS: return False, "too_many_attempts"
    if not secrets.compare_digest(otp.code, code):
        otp.attempts += 1; otp.save(update_fields=["attempts"])
        return False, "wrong_code"
    otp.used_at = timezone.now(); otp.save(update_fields=["used_at"])
    return True, "ok"
''')

# ------------------------------------------------------------------
# 3. accounts/sms.py
# ------------------------------------------------------------------
print("\n[3/12] accounts/sms.py")
write("accounts/sms.py", r'''
"""SMS sender. Dev: console. Prod: Hubtel (set SMS_BACKEND=hubtel)."""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def _send_console(phone, message):
    print(f"\n[SMS → {phone}]\n{message}\n")
    return True


def _send_hubtel(phone, message):
    try:
        import requests
    except ImportError:
        logger.error("requests not installed; cannot send SMS")
        return False
    try:
        r = requests.get(
            "https://smsc.hubtel.com/v1/messages/send",
            params={
                "clientid": settings.HUBTEL_CLIENT_ID,
                "clientsecret": settings.HUBTEL_CLIENT_SECRET,
                "from": settings.HUBTEL_SENDER_ID,
                "to": phone,
                "content": message,
            },
            timeout=15,
        )
        r.raise_for_status()
        return True
    except Exception as e:
        logger.exception("Hubtel SMS failed: %s", e)
        return False


BACKENDS = {"console": _send_console, "hubtel": _send_hubtel}


def send_sms(phone, message):
    backend = BACKENDS.get(getattr(settings, "SMS_BACKEND", "console"), _send_console)
    return backend(phone, message)


def send_otp_sms(phone, code):
    return send_sms(phone, f"Your Tumakonect verification code is {code}. Valid for 5 minutes.")
''')

# ------------------------------------------------------------------
# 4. accounts/serializers_otp.py
# ------------------------------------------------------------------
print("\n[4/12] accounts/serializers_otp.py")
write("accounts/serializers_otp.py", r'''
from rest_framework import serializers

PHONE_RE = r"^\+?[0-9]{9,15}$"


class SendOTPSerializer(serializers.Serializer):
    phone = serializers.RegexField(PHONE_RE, error_messages={"invalid": "Enter a valid phone number."})
    def validate_phone(self, value):
        return value.replace(" ", "").replace("-", "")


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.RegexField(PHONE_RE)
    code = serializers.RegexField(r"^[0-9]{6}$")
    def validate_phone(self, value):
        return value.replace(" ", "").replace("-", "")
''')

# ------------------------------------------------------------------
# 5. accounts/views_otp.py
# ------------------------------------------------------------------
print("\n[5/12] accounts/views_otp.py")
write("accounts/views_otp.py", r'''
"""Client OTP endpoints: send / resend / verify."""
from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .otp import issue_otp, verify_otp
from .serializers_otp import SendOTPSerializer, VerifyOTPSerializer
from .sms import send_otp_sms

try:
    from customers.models import Customer
except Exception:
    Customer = None


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff: return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _get_or_create_client(phone):
    phone = phone.strip()
    user = User.objects.filter(phone=phone).first()
    if user is None:
        user = User.objects.create(
            username=phone, phone=phone,
            user_type="CLIENT", is_active=True,
        )
        user.set_unusable_password()
        user.save(update_fields=["password"])

    if user.user_type != "CLIENT":
        raise PermissionError("This number belongs to a staff account.")

    customer = None
    if Customer is not None:
        customer = Customer.objects.filter(phone=phone).first()
        if customer is None:
            customer = Customer.objects.create(
                name="", phone=phone, user=user,
                created_by=user, updated_by=user,
            )
        elif customer.user_id is None:
            customer.user = user
            customer.save(update_fields=["user", "updated_at"])
        elif customer.user_id != user.id:
            raise PermissionError("This phone is linked to a different account.")
    return user, customer


class SendOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "otp_send"

    def post(self, request):
        ser = SendOTPSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        phone = ser.validated_data["phone"]

        existing = User.objects.filter(phone=phone).first()
        if existing and existing.user_type != "CLIENT":
            return Response({"detail": "This number belongs to a staff account."},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            code = issue_otp(phone, ip=_client_ip(request), purpose="login")
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        sent = send_otp_sms(phone, code)
        body = {"ok": True, "detail": "Code sent.", "expires_in": 300}
        if settings.DEBUG:
            body["debug_code"] = code
        return Response(body, status=status.HTTP_200_OK if sent else status.HTTP_502_BAD_GATEWAY)


class ResendOTPView(SendOTPView):
    pass


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        ser = VerifyOTPSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        phone = ser.validated_data["phone"]
        code = ser.validated_data["code"]

        ok, reason = verify_otp(phone, code, purpose="login")
        if not ok:
            msgs = {
                "no_code": "No code was requested for this number.",
                "expired": "This code has expired. Request a new one.",
                "too_many_attempts": "Too many incorrect attempts.",
                "wrong_code": "Incorrect code.",
                "already_used": "This code has already been used.",
            }
            return Response({"detail": msgs.get(reason, "Verification failed.")},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user, customer = _get_or_create_client(phone)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id, "username": user.username,
                "phone": user.phone, "user_type": user.user_type,
                "customer_id": customer.id if customer else None,
            },
        })
''')

# ------------------------------------------------------------------
# 6. accounts/client_urls.py
# ------------------------------------------------------------------
print("\n[6/12] accounts/client_urls.py")
write("accounts/client_urls.py", r'''
from django.urls import path
from .views_otp import ResendOTPView, SendOTPView, VerifyOTPView

app_name = "client_auth"

urlpatterns = [
    path("otp/send/", SendOTPView.as_view(), name="otp_send"),
    path("otp/resend/", ResendOTPView.as_view(), name="otp_resend"),
    path("otp/verify/", VerifyOTPView.as_view(), name="otp_verify"),
]
''')

# ------------------------------------------------------------------
# 7. accounts/admin.py
# ------------------------------------------------------------------
print("\n[7/12] accounts/admin.py")
p = ROOT / "accounts/admin.py"
if p.exists():
    text = p.read_text(encoding="utf-8")
    if "OTPCode" not in text:
        bkp("accounts/admin.py")
        text = text.rstrip() + r'''


from .models import OTPCode  # noqa: E402


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ("phone", "code", "purpose", "attempts", "used_at", "created_at")
    list_filter = ("purpose", "used_at")
    search_fields = ("phone",)
    date_hierarchy = "created_at"
    readonly_fields = ("phone", "code", "purpose", "attempts",
                       "used_at", "created_at", "ip_address")
'''
        p.write_text(text, encoding="utf-8")
        print("  updated accounts/admin.py")
    else:
        print("  skip    accounts/admin.py")

# ------------------------------------------------------------------
# 8. management command
# ------------------------------------------------------------------
print("\n[8/12] send_test_sms command")
write("accounts/management/__init__.py", "")
write("accounts/management/commands/__init__.py", "")
write("accounts/management/commands/send_test_sms.py", r'''
from django.core.management.base import BaseCommand
from accounts.sms import send_sms


class Command(BaseCommand):
    help = "Send a test SMS via the configured backend."

    def add_arguments(self, parser):
        parser.add_argument("phone")
        parser.add_argument("--message", default="Tumakonect test message")

    def handle(self, *args, **opts):
        ok = send_sms(opts["phone"], opts["message"])
        self.stdout.write(self.style.SUCCESS("sent") if ok else self.style.ERROR("failed"))
''')

# ------------------------------------------------------------------
# 9. customers/models.py
# ------------------------------------------------------------------
print("\n[9/12] customers/models.py")
p = ROOT / "customers/models.py"
if p.exists():
    text = p.read_text(encoding="utf-8")
    mod = False

    if "user = models.OneToOneField" not in text:
        marker = "    )\n    notes = models.TextField"
        if marker in text:
            user_field = """    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='customer',
        help_text="Linked app account. Null for call-center-only customers.",
    )
    notes = models.TextField"""
            text = text.replace(marker, user_field, 1)
            mod = True
            print("  + user OneToOneField")

    if "phone = models.CharField" in text and "unique=True" not in text.split("phone = models.CharField")[1].split(")")[0]:
        text = re.sub(
            r"(phone\s*=\s*models\.CharField\([^)]*?)db_index=True",
            r"\1unique=True,\n        db_index=True",
            text, count=1,
        )
        mod = True
        print("  + phone unique=True")

    if mod:
        bkp("customers/models.py")
        p.write_text(text, encoding="utf-8")

# ------------------------------------------------------------------
# 10. customers/serializers.py + views.py + admin.py
# ------------------------------------------------------------------
print("\n[10/12] customers serializers/views/admin")

bkp("customers/serializers.py")
write("customers/serializers.py", r'''
from rest_framework import serializers
from .models import Customer


class CustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name", "phone", "email", "address",
                  "organization", "created_at", "is_deleted"]
        read_only_fields = ["id", "created_at", "updated_at"]


class CustomerDetailSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True, default=None)
    has_account = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ["id", "name", "phone", "email", "address",
                  "gps_lat", "gps_lng", "organization", "organization_name",
                  "notes", "tags", "user", "has_account",
                  "created_at", "updated_at", "created_by", "updated_by",
                  "is_deleted", "deleted_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at",
                            "created_by", "updated_by", "is_deleted", "deleted_at"]

    def get_has_account(self, obj):
        return obj.user_id is not None


class CustomerCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["name", "phone", "email", "address",
                  "gps_lat", "gps_lng", "organization", "notes", "tags"]

    def validate_phone(self, value):
        value = (value or "").strip()
        qs = Customer.objects.filter(phone=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A customer with this phone already exists.")
        return value

    def create(self, validated_data):
        req = self.context.get("request")
        if req and getattr(req.user, "is_authenticated", False):
            validated_data["created_by"] = req.user
            validated_data["updated_by"] = req.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        req = self.context.get("request")
        if req and getattr(req.user, "is_authenticated", False):
            validated_data["updated_by"] = req.user
        return super().update(instance, validated_data)
''')

bkp("customers/views.py")
write("customers/views.py", r'''
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsAgent, IsDispatcher
from .models import Customer
from .serializers import (
    CustomerCreateUpdateSerializer,
    CustomerDetailSerializer,
    CustomerListSerializer,
)

STAFF_TYPES = {"ADMIN", "AGENT", "DISPATCHER", "SUPERVISOR", "MANAGER"}


class IsStaffOrOwner(permissions.BasePermission):
    message = "You do not have access to this customer."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        u = request.user
        ut = (getattr(u, "user_type", "") or "").upper()
        if ut in STAFF_TYPES: return True
        if ut == "CLIENT": return obj.user_id == u.id
        if ut == "ARTISAN": return request.method in permissions.SAFE_METHODS
        return False


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["organization", "is_deleted"]
    search_fields = ["name", "phone", "email", "address"]
    ordering_fields = ["name", "created_at", "phone"]
    ordering = ["-created_at"]
    lookup_value_regex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

    def get_queryset(self):
        qs = Customer.objects.filter(is_deleted=False).select_related("user", "organization")
        u = self.request.user
        ut = (getattr(u, "user_type", "") or "").upper()
        if ut in STAFF_TYPES: return qs
        if ut == "CLIENT": return qs.filter(user=u)
        if ut == "ARTISAN":
            return qs.filter(invoices__incident__assignments__artisan=u).distinct()
        return qs.none()

    def get_serializer_class(self):
        if self.action == "list": return CustomerListSerializer
        if self.action in ("create", "update", "partial_update"): return CustomerCreateUpdateSerializer
        return CustomerDetailSerializer

    def get_permissions(self):
        if self.action in ("create", "destroy", "restore"):
            self.permission_classes = [IsAgent | IsAdmin]
        elif self.action in ("update", "partial_update"):
            self.permission_classes = [IsAgent | IsAdmin | IsStaffOrOwner]
        elif self.action == "search_customers":
            self.permission_classes = [IsAgent | IsAdmin | IsDispatcher]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        u = request.user
        ut = (getattr(u, "user_type", "") or "").upper()
        if ut != "CLIENT":
            return Response({"detail": "Only client accounts can use this endpoint."},
                            status=status.HTTP_403_FORBIDDEN)
        customer = Customer.objects.filter(user=u, is_deleted=False).first()
        if not customer:
            return Response({"detail": "No customer profile linked to this account."},
                            status=status.HTTP_404_NOT_FOUND)
        if request.method == "PATCH":
            ALLOWED = {"name", "email", "address", "gps_lat", "gps_lng"}
            data = {k: v for k, v in request.data.items() if k in ALLOWED}
            ser = CustomerCreateUpdateSerializer(customer, data=data, partial=True,
                                                 context={"request": request})
            ser.is_valid(raise_exception=True)
            ser.save(updated_by=u)
            return Response(CustomerDetailSerializer(customer).data)
        return Response(CustomerDetailSerializer(customer).data)

    @action(detail=False, methods=["get"], url_path="search", url_name="search")
    def search_customers(self, request):
        query = (request.query_params.get("q") or "").strip()
        if not query:
            return Response({"results": []})
        customers = Customer.objects.filter(
            Q(name__icontains=query) | Q(phone__icontains=query) | Q(email__icontains=query),
            is_deleted=False,
        )[:20]
        return Response({"results": CustomerListSerializer(customers, many=True).data})

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        customer = Customer.objects.get(pk=pk, is_deleted=True)
        customer.restore()
        return Response({"status": "restored"})
''')

bkp("customers/admin.py")
write("customers/admin.py", r'''
from django import forms
from django.contrib import admin, messages
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from .models import Customer


class LinkUserForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    phone = forms.CharField(max_length=20, help_text="Phone number of the CLIENT user to link.")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "organization",
                    "has_account", "created_at", "is_deleted", "created_by")
    list_filter = ("is_deleted", "organization", "created_at", "created_by")
    search_fields = ("name", "phone", "email", "address", "notes", "tags",
                     "user__username", "user__email")
    raw_id_fields = ("user", "organization")
    readonly_fields = ("id", "user", "created_at", "updated_at",
                       "created_by", "updated_by", "deleted_at")
    ordering = ("-created_at",)
    list_per_page = 25

    fieldsets = (
        (None, {"fields": ("name", "phone", "email", "address")}),
        (_("Location"), {"fields": ("gps_lat", "gps_lng"), "classes": ("collapse",)}),
        (_("Organization"), {"fields": ("organization",)}),
        (_("App account"), {"fields": ("user",),
                            "description": "Linked when client logs in via OTP."}),
        (_("Metadata"), {"fields": ("notes", "tags")}),
        (_("Audit"), {"fields": ("id", "created_at", "updated_at",
                                 "created_by", "updated_by",
                                 "is_deleted", "deleted_at"),
                      "classes": ("collapse",)}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj: return self.readonly_fields + ("created_by", "updated_by")
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change: obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    @admin.display(boolean=True, description="App account")
    def has_account(self, obj): return obj.user_id is not None

    @admin.action(description="Soft-delete selected customers", permissions=["delete"])
    def soft_delete_selected(self, request, qs):
        n = qs.update(is_deleted=True, deleted_at=timezone.now())
        self.message_user(request, f"{n} customer(s) soft-deleted.")

    @admin.action(description="Restore selected customers", permissions=["delete"])
    def restore_selected(self, request, qs):
        n = qs.update(is_deleted=False, deleted_at=None)
        self.message_user(request, f"{n} customer(s) restored.")

    @admin.action(description="Export selected customers as CSV", permissions=["view"])
    def export_csv(self, request, qs):
        import csv
        from django.http import HttpResponse
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="customers.csv"'
        w = csv.writer(resp)
        w.writerow(["ID", "Name", "Phone", "Email", "Address",
                    "Organization", "Has App Account", "Created At", "Is Deleted"])
        for c in qs.select_related("organization", "user"):
            w.writerow([c.id, c.name, c.phone, c.email, c.address,
                        c.organization.name if c.organization else "",
                        "Yes" if c.user_id else "No", c.created_at,
                        "Yes" if c.is_deleted else "No"])
        return resp

    @admin.action(description="Link to app account by phone", permissions=["change"])
    def link_to_user(self, request, qs):
        form = None
        if "apply" in request.POST:
            form = LinkUserForm(request.POST)
            if form.is_valid():
                phone = form.cleaned_data["phone"].strip().replace(" ", "").replace("-", "")
                user = User.objects.filter(phone=phone, user_type="CLIENT").first()
                if not user:
                    self.message_user(request, f"No CLIENT user with phone {phone}.",
                                      level=messages.ERROR)
                else:
                    linked = skipped = already = 0
                    for c in qs:
                        if c.user_id == user.id: already += 1; continue
                        if c.user_id and c.user_id != user.id: skipped += 1; continue
                        c.user = user; c.updated_by = request.user
                        c.save(update_fields=["user", "updated_by", "updated_at"])
                        linked += 1
                    parts = []
                    if linked: parts.append(f"{linked} linked")
                    if already: parts.append(f"{already} already linked")
                    if skipped: parts.append(f"{skipped} skipped")
                    self.message_user(request, f"Linked to {user}: {', '.join(parts) or 'no changes'}.",
                                      level=messages.SUCCESS if linked else messages.WARNING)
        if form is None:
            form = LinkUserForm(initial={"_selected_action": request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
        return render(request, "admin/customers/link_user_form.html",
                      {"items": qs, "form": form,
                       "title": "Link selected customers to app account",
                       "opts": self.model._meta})

    actions = [soft_delete_selected, restore_selected, export_csv, link_to_user]
''')

write("customers/templates/admin/customers/link_user_form.html", r'''
{% extends "admin/base_site.html" %}
{% block content %}
  <h1>{{ title }}</h1>
  <p>Linking <strong>{{ items|length }}</strong> customer(s) to a CLIENT app account.</p>
  <ul>{% for c in items %}<li><strong>{{ c.name|default:"(no name)" }}</strong> — {{ c.phone }}</li>{% endfor %}</ul>
  <form method="post">
    {% csrf_token %}
    {% for field in form.hidden_fields %}{{ field }}{% endfor %}
    <div style="margin:20px 0;padding:16px;background:#f8fafc;border-radius:8px;">
      <label for="{{ form.phone.id_for_label }}" style="display:block;font-weight:600;margin-bottom:6px;">{{ form.phone.label }}</label>
      {{ form.phone }}
      {% if form.phone.help_text %}<p style="color:#64748b;margin-top:6px;">{{ form.phone.help_text }}</p>{% endif %}
    </div>
    <input type="hidden" name="apply" value="1" />
    <input type="submit" class="default" value="Link" />
    <a href="{% url 'admin:customers_customer_changelist' %}" style="margin-left:12px;">Cancel</a>
  </form>
{% endblock %}
''')

# ------------------------------------------------------------------
# 11. settings + urls
# ------------------------------------------------------------------
print("\n[11/12] settings + urls")

s = find_settings()
if s:
    append_once(s, "# === CLIENT OTP ===", r'''
# === CLIENT OTP ===
import os as _os
SMS_BACKEND = _os.environ.get("SMS_BACKEND", "console")
HUBTEL_CLIENT_ID = _os.environ.get("HUBTEL_CLIENT_ID", "")
HUBTEL_CLIENT_SECRET = _os.environ.get("HUBTEL_CLIENT_SECRET", "")
HUBTEL_SENDER_ID = _os.environ.get("HUBTEL_SENDER_ID", "Tumakonect")
OTP_TTL_SECONDS = 300
OTP_MAX_ATTEMPTS = 3
OTP_MAX_PER_HOUR = 5
OTP_MAX_PER_HOUR_PER_IP = 20
CACHES = {"default": {"BACKEND": _os.environ.get(
    "CACHE_BACKEND", "django.core.cache.backends.locmem.LocMemCache"),
    "LOCATION": _os.environ.get("CACHE_LOCATION", "otp-cache")}}
# === /CLIENT OTP ===
''')
    append_once(s, "# === OTP THROTTLE ===", r'''
# === OTP THROTTLE ===
REST_FRAMEWORK = dict(globals().get("REST_FRAMEWORK", {}))
REST_FRAMEWORK.setdefault("DEFAULT_THROTTLE_CLASSES", [])
REST_FRAMEWORK.setdefault("DEFAULT_THROTTLE_RATES", {})
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["otp_send"] = "5/hour"
# === /OTP THROTTLE ===
''')

u = find_root_urls()
if u and (ROOT / u).exists():
    p = ROOT / u
    text = p.read_text(encoding="utf-8")
    if "accounts.client_urls" not in text:
        if "from django.urls import" in text and "include" not in text.split("from django.urls import")[1].split("\n")[0]:
            text = text.replace("from django.urls import", "from django.urls import include,", 1)
        line = '    path("api/auth/", include("accounts.client_urls", namespace="client_auth")),\n'
        for needle in ("\n]", "\r\n]", "\n]\n"):
            if needle in text:
                text = text.replace(needle, line + needle, 1); break
        bkp(u); p.write_text(text, encoding="utf-8")
        print(f"  updated {u}")

# ------------------------------------------------------------------
# 12. React
# ------------------------------------------------------------------
print("\n[12/12] React — auth screens")

write(f"{REACT_SRC}/api/authClient.js", r'''
import axios from 'axios';

const BASE = import.meta?.env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';
const authClient = axios.create({ baseURL: BASE });

export const sendOtp = (phone) => authClient.post('/auth/otp/send/', { phone }).then(r => r.data);
export const resendOtp = (phone) => authClient.post('/auth/otp/resend/', { phone }).then(r => r.data);
export const verifyOtp = (phone, code) => authClient.post('/auth/otp/verify/', { phone, code }).then(r => r.data);
export default authClient;
''')

write(f"{REACT_SRC}/screens/auth/PhoneEntryScreen.jsx", r'''
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaPhoneAlt, FaArrowRight, FaCircleNotch } from 'react-icons/fa';
import { sendOtp } from '../../api/authClient';
import './auth.css';

const PHONE_RE = /^\+?[0-9]{9,15}$/;

export default function PhoneEntryScreen() {
  const navigate = useNavigate();
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    const cleaned = phone.replace(/[\s-]/g, '');
    if (!PHONE_RE.test(cleaned)) { setError('Enter a valid phone number.'); return; }
    setLoading(true);
    try {
      const res = await sendOtp(cleaned);
      navigate('/login-otp', { state: { phone: cleaned, debugCode: res?.debug_code } });
    } catch (e) {
      setError(e?.response?.data?.detail || 'Could not send code.');
    } finally { setLoading(false); }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-hero">
          <div className="auth-hero__icon"><FaPhoneAlt /></div>
          <h1>Sign in</h1>
          <p>Enter your phone number. We'll text you a 6-digit code.</p>
        </div>

        <form onSubmit={submit} className="auth-form">
          <div className="auth-field">
            <label htmlFor="phone">Phone number</label>
            <input
              id="phone" type="tel" inputMode="tel"
              value={phone} onChange={(e) => { setPhone(e.target.value); setError(''); }}
              placeholder="+233 24 000 0000" autoFocus autoComplete="tel"
            />
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button type="submit" className="auth-btn" disabled={loading || !phone}>
            {loading ? <><FaCircleNotch className="auth-spin" /> Sending…</> : <>Continue <FaArrowRight /></>}
          </button>
        </form>
      </div>
    </div>
  );
}
''')

write(f"{REACT_SRC}/screens/auth/OtpVerifyScreen.jsx", r'''
import { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { FaCircleNotch, FaArrowLeft } from 'react-icons/fa';
import { verifyOtp, resendOtp } from '../../api/authClient';
import { useAuth } from '../../context/AuthContext';
import './auth.css';

export default function OtpVerifyScreen() {
  const navigate = useNavigate();
  const location = useLocation();
  const { loginWithToken } = useAuth() || {};
  const phone = location.state?.phone || '';
  const debugCode = location.state?.debugCode || '';

  const [code, setCode] = useState(debugCode || '');
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [seconds, setSeconds] = useState(60);
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  useEffect(() => { if (!phone) navigate('/login-phone', { replace: true }); }, [phone, navigate]);
  useEffect(() => { inputRef.current?.focus(); }, []);
  useEffect(() => {
    if (seconds <= 0) return;
    const t = setInterval(() => setSeconds(s => s - 1), 1000);
    return () => clearInterval(t);
  }, [seconds]);

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    if (!/^[0-9]{6}$/.test(code)) { setError('Enter the 6-digit code.'); return; }
    setLoading(true);
    try {
      const res = await verifyOtp(phone, code);
      if (loginWithToken) await loginWithToken(res);
      else {
        localStorage.setItem('accessToken', res.access);
        localStorage.setItem('refreshToken', res.refresh);
        localStorage.setItem('user_type', res.user.user_type);
      }
      navigate('/client/invoices', { replace: true });
    } catch (e) {
      setError(e?.response?.data?.detail || 'Verification failed.');
    } finally { setLoading(false); }
  };

  const resend = async () => {
    setResending(true); setError('');
    try {
      const res = await resendOtp(phone);
      setSeconds(60);
      if (res?.debug_code) setCode(res.debug_code);
    } catch (e) {
      setError(e?.response?.data?.detail || 'Could not resend.');
    } finally { setResending(false); }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <Link to="/login-phone" className="auth-back"><FaArrowLeft /> Change number</Link>
        <div className="auth-hero">
          <h1>Enter the code</h1>
          <p>We sent a 6-digit code to <strong>{phone}</strong>.</p>
        </div>

        <form onSubmit={submit} className="auth-form">
          <div className="auth-field">
            <label htmlFor="code">Verification code</label>
            <input
              id="code" ref={inputRef} type="text" inputMode="numeric"
              pattern="[0-9]*" maxLength={6}
              value={code}
              onChange={(e) => { setCode(e.target.value.replace(/[^0-9]/g, '')); setError(''); }}
              className="auth-code"
              placeholder="000000"
            />
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button type="submit" className="auth-btn" disabled={loading || code.length !== 6}>
            {loading ? <><FaCircleNotch className="auth-spin" /> Verifying…</> : 'Verify & sign in'}
          </button>

          <div className="auth-resend">
            {seconds > 0 ? (
              <span>Resend in <strong>{seconds}s</strong></span>
            ) : (
              <button type="button" onClick={resend} disabled={resending}>
                {resending ? 'Sending…' : 'Resend code'}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
''')

write(f"{REACT_SRC}/screens/auth/auth.css", r'''
:root {
  color-scheme: light;
  --a-ink: #0b1226; --a-ink-500: #64748b; --a-line: #e8ecf5;
  --a-blue: #0a35d6; --a-blue-soft: #eef1fb; --a-red: #ef4444; --a-red-soft: #fef2f2;
  --a-font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
.auth-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  padding: 24px 16px;
  background: radial-gradient(900px 500px at 10% -10%, rgba(10,53,214,0.08), transparent 60%),
              linear-gradient(180deg, #f7f8fc 0%, #eef1f9 100%);
  font-family: var(--a-font); color: var(--a-ink);
}
.auth-card {
  width: 100%; max-width: 400px; padding: 32px 28px;
  background: #fff; border: 1px solid var(--a-line); border-radius: 22px;
  box-shadow: 0 20px 50px -20px rgba(15,23,42,0.18);
  display: flex; flex-direction: column; gap: 22px;
}
.auth-back {
  align-self: flex-start; display: inline-flex; align-items: center; gap: 6px;
  font-size: 12.5px; font-weight: 600; color: var(--a-blue); text-decoration: none;
}
.auth-hero { display: flex; flex-direction: column; gap: 8px; }
.auth-hero__icon {
  width: 52px; height: 52px; border-radius: 16px; display: grid; place-items: center;
  background: linear-gradient(135deg, #0a35d6, #1a4dff); color: #fff; font-size: 20px;
  box-shadow: 0 14px 28px -14px rgba(10,53,214,0.65); margin-bottom: 4px;
}
.auth-hero h1 { margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.8px; }
.auth-hero p { margin: 0; font-size: 14px; color: var(--a-ink-500); line-height: 1.55; }
.auth-hero strong { color: var(--a-ink); font-weight: 700; }

.auth-form { display: flex; flex-direction: column; gap: 16px; }
.auth-field { display: flex; flex-direction: column; gap: 6px; }
.auth-field label {
  font-size: 12.5px; font-weight: 700; letter-spacing: 0.2px; color: #334155;
}
.auth-field input {
  font: inherit; font-size: 15px; padding: 13px 16px; border-radius: 14px;
  border: 1.5px solid var(--a-line); background: #fbfcff; color: var(--a-ink);
  outline: none; transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.auth-field input:focus { border-color: var(--a-blue); background: #fff;
  box-shadow: 0 0 0 4px rgba(10,53,214,0.12); }
.auth-field input.auth-code {
  font-size: 24px; font-weight: 800; letter-spacing: 8px; text-align: center;
  padding: 16px; font-variant-numeric: tabular-nums;
}

.auth-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  padding: 14px 20px; font: inherit; font-size: 14.5px; font-weight: 700;
  border-radius: 14px; border: 0; cursor: pointer;
  background: linear-gradient(135deg, #0a35d6, #1a4dff); color: #fff;
  box-shadow: 0 14px 28px -14px rgba(10,53,214,0.75); transition: transform 0.2s ease;
}
.auth-btn:hover:not(:disabled) { transform: translateY(-1px); }
.auth-btn:disabled { opacity: 0.55; cursor: not-allowed; }

.auth-error { margin: 0; font-size: 13px; font-weight: 600; color: var(--a-red); }

.auth-resend { text-align: center; font-size: 13px; color: var(--a-ink-500); }
.auth-resend button {
  background: none; border: 0; color: var(--a-blue); font: inherit;
  font-weight: 700; cursor: pointer; padding: 4px 8px;
}
.auth-resend strong { color: var(--a-ink); }

.auth-spin { animation: auth-spin 0.9s linear infinite; }
@keyframes auth-spin { to { transform: rotate(360deg); } }
''')

# Patch App.jsx
app = None
for c in (f"{REACT_SRC}/App.jsx", f"{REACT_SRC}/App.tsx", f"{REACT_SRC}/routes.jsx"):
    if (ROOT / c).exists(): app = c; break

if app:
    p = ROOT / app
    text = p.read_text(encoding="utf-8")
    if "/login-phone" not in text:
        imports = '''import PhoneEntryScreen from './screens/auth/PhoneEntryScreen';
import OtpVerifyScreen from './screens/auth/OtpVerifyScreen';
'''
        lines = text.split("\n")
        last_import = 0
        for i, l in enumerate(lines):
            if l.startswith("import "): last_import = i
        lines.insert(last_import + 1, imports.rstrip())
        text = "\n".join(lines)

        routes = '''
          <Route path="/login-phone" element={<PhoneEntryScreen />} />
          <Route path="/login-otp" element={<OtpVerifyScreen />} />
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

1. Check for duplicate phones before migrating:
       python manage.py shell
       >>> from accounts.models import User
       >>> from customers.models import Customer
       >>> from django.db.models import Count
       >>> User.objects.exclude(phone__isnull=True).values('phone').annotate(n=Count('id')).filter(n__gt=1)
       >>> Customer.objects.values('phone').annotate(n=Count('id')).filter(n__gt=1)

2. Migrate:
       python manage.py makemigrations accounts customers
       python manage.py migrate

3. Test OTP:
       curl -X POST http://127.0.0.1:8000/api/auth/otp/send/ \\
         -H "Content-Type: application/json" -d '{"phone":"+233240000000"}'

4. In the browser:
       http://localhost:5173/login-phone
""")