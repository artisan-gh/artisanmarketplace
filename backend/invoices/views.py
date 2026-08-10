from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Invoice, InvoiceItem
from .serializers import (
    InvoiceSerializer,
    InvoiceListSerializer,
    InvoiceCreateSerializer,
    InvoiceSendSerializer,
    InvoiceItemSerializer,
)


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for invoices.
    """
    queryset = Invoice.objects.select_related('client', 'booking', 'payment').prefetch_related('items').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'client', 'booking', 'currency']
    search_fields = ['invoice_number', 'client__email', 'booking__reference']
    ordering_fields = ['issued_date', 'due_date', 'total', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        if self.action == 'create':
            return InvoiceCreateSerializer
        return InvoiceSerializer

    def perform_create(self, serializer):
        # Ensure the client is not the same as the booking client? We'll trust the input.
        # Could add validation that client matches booking.client.user
        serializer.save()

    # ─── Custom Actions ──────────────────────────────────────

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """
        Send the invoice (mark as sent, optionally email).
        """
        invoice = self.get_object()
        serializer = InvoiceSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            invoice.send()
            # If send_email is True, trigger email sending (placeholder)
            if serializer.validated_data.get('send_email', False):
                # Integrate with email/notification system here
                pass
            return Response({
                'status': 'sent',
                'invoice': InvoiceSerializer(invoice).data
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """
        Mark the invoice as paid, optionally linking a payment.
        """
        invoice = self.get_object()
        payment_id = request.data.get('payment_id')
        payment = None
        if payment_id:
            from payments.models import Payment
            payment = get_object_or_404(Payment, id=payment_id)
        try:
            invoice.mark_paid(payment)
            return Response({
                'status': 'paid',
                'invoice': InvoiceSerializer(invoice).data
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel the invoice.
        """
        invoice = self.get_object()
        try:
            invoice.cancel()
            return Response({
                'status': 'cancelled',
                'invoice': InvoiceSerializer(invoice).data
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """
        Placeholder for PDF download.
        """
        invoice = self.get_object()
        # Here you would generate a PDF using something like ReportLab or WeasyPrint
        # Return a dummy response for now
        return Response({
            'message': 'PDF generation not implemented yet.',
            'invoice_number': invoice.invoice_number
        })

    @action(detail=False, methods=['get'])
    def my_invoices(self, request):
        """
        Get invoices for the current user.
        """
        invoices = self.get_queryset().filter(client=request.user)
        serializer = self.get_serializer(invoices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get overdue invoices for the current user.
        """
        invoices = self.get_queryset().filter(
            client=request.user,
            status__in=[Invoice.InvoiceStatus.SENT, Invoice.InvoiceStatus.PARTIALLY_PAID],
            due_date__lt=timezone.now().date()
        )
        serializer = self.get_serializer(invoices, many=True)
        return Response(serializer.data)
