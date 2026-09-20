
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
