"""Client OTP endpoints: send / resend / verify."""
import uuid

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
except ImportError:
    Customer = None


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _client_email(phone):
    """
    Your User model identifies users by email, not username.
    Generate a placeholder email for phone-only client signups.
    """
    digits = "".join(c for c in phone if c.isdigit())
    return f"client-{digits}@noreply.tumakonect.local"


def _get_or_create_client(phone):
    phone = (phone or "").strip()

    user = User.objects.filter(phone_number=phone).first()
    if user is None:
        user = User.objects.create(
            email=_client_email(phone),
            phone_number=phone,
            user_type="CLIENT",
            is_active=True,
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
                name="",
                phone=phone,
                user=user,
                created_by=user,
                updated_by=user,
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

        existing = User.objects.filter(phone_number=phone).first()
        if existing and existing.user_type != "CLIENT":
            return Response(
                {"detail": "This number belongs to a staff account. "
                           "Use the staff portal."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            code = issue_otp(phone, ip=_client_ip(request), purpose="login")
        except ValueError as e:
            return Response({"detail": str(e)},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        sent = send_otp_sms(phone, code)

        body = {"ok": True, "detail": "Code sent.", "expires_in": 300}
        if settings.DEBUG:
            body["debug_code"] = code

        return Response(
            body,
            status=status.HTTP_200_OK if sent else status.HTTP_502_BAD_GATEWAY,
        )


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
            messages = {
                "no_code": "No code was requested for this number.",
                "expired": "This code has expired. Request a new one.",
                "too_many_attempts": "Too many incorrect attempts.",
                "wrong_code": "Incorrect code.",
                "already_used": "This code has already been used.",
            }
            return Response({"detail": messages.get(reason, "Verification failed.")},
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
                "id": user.id,
                "email": user.email,
                "phone": user.phone_number,
                "user_type": user.user_type,
                "customer_id": customer.id if customer else None,
            },
        })
