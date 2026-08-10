import uuid
import requests
import json
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Payment
from .serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentInitiateSerializer,
    PaymentRefundSerializer,
    PaymentWebhookSerializer,
    WalletTopUpSerializer,
)
from wallets.models import Wallet


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for payments.
    """
    queryset = Payment.objects.select_related('user').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method']
    search_fields = ['transaction_reference', 'gateway_reference']
    ordering_fields = ['amount', 'paid_at', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ─── Initiate Payment (removed booking dependency) ──────

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def initiate(self, request):
        """
        Initiate a new payment.
        NOTE: Booking integration is temporarily disabled.
        Use wallet_topup for wallet funding.
        """
        return Response(
            {
                'error': 'Booking payments are currently disabled. Please use the wallet top‑up endpoint.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ─── Wallet Top‑up ──────────────────────────────────────

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def wallet_topup(self, request):
        """
        Initiate a wallet top‑up for the authenticated user.
        No booking involved – credits the user's wallet upon success.
        """
        serializer = WalletTopUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data['amount']
        currency = serializer.validated_data.get('currency', 'GHS')
        description = serializer.validated_data.get('description', '')

        # Ensure the user has a wallet (lazy creation)
        wallet, created = Wallet.objects.get_or_create(
            user=request.user,
            defaults={
                'balance': 0.00,
                'currency': currency,
                'total_earned': 0.00,
                'total_withdrawn': 0.00,
            }
        )

        # Create a Payment record for the top‑up (booking = None)
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            currency=currency,
            description=description or f'Wallet top-up of {currency} {amount:.2f}',
            transaction_reference=f'TOPUP-{uuid.uuid4().hex[:8].upper()}',
            status=Payment.PaymentStatus.PENDING,
            payment_method='CARD',
        )

        # Integrate with Paystack
        paystack_secret = getattr(settings, 'PAYSTACK_SECRET_KEY', None)
        if not paystack_secret:
            payment.mark_failed({'error': 'Paystack secret key not configured.'})
            return Response(
                {'error': 'Payment gateway not configured. Please contact support.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        paystack_url = 'https://api.paystack.co/transaction/initialize'
        headers = {
            'Authorization': f'Bearer {paystack_secret}',
            'Content-Type': 'application/json',
        }
        callback_url = f"{settings.BACKEND_URL}/api/payments/verify/"
        data = {
            'amount': int(amount * 100),
            'email': request.user.email,
            'reference': payment.transaction_reference,
            'callback_url': callback_url,
            'currency': currency,
            'metadata': {
                'payment_id': payment.id,
                'type': 'wallet_topup',
            },
        }

        try:
            resp = requests.post(paystack_url, json=data, headers=headers, timeout=30)
            resp.raise_for_status()
            result = resp.json()
        except requests.exceptions.RequestException as e:
            payment.mark_failed({'error': str(e)})
            return Response(
                {'error': 'Could not connect to payment gateway. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if not result.get('status'):
            payment.mark_failed(result)
            error_msg = result.get('message', 'Payment initialization failed.')
            return Response(
                {'error': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        gateway_ref = result['data']['reference']
        payment.gateway_reference = gateway_ref
        payment.initiate(gateway_ref)

        return Response({
            'payment': PaymentSerializer(payment).data,
            'authorization_url': result['data']['authorization_url'],
            'gateway_reference': gateway_ref,
        }, status=status.HTTP_200_OK)

    # ─── Verify (callback from Paystack) ──────────────────────

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def verify(self, request):
        """
        Verify a payment after the user returns from the payment gateway.
        Query params: ?reference=TOPUP-XXXX&trxref=TOPUP-XXXX (Paystack sends both)
        """
        reference = request.GET.get('reference') or request.GET.get('trxref')
        if not reference:
            return Response({'error': 'Missing payment reference'}, status=400)

        try:
            payment = Payment.objects.get(transaction_reference=reference)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=404)

        # If already successful, redirect to frontend with success
        if payment.is_successful:
            return redirect(f"{settings.FRONTEND_URL}/wallet?status=success")

        # Call Paystack to verify the transaction
        paystack_secret = getattr(settings, 'PAYSTACK_SECRET_KEY', None)
        if not paystack_secret:
            payment.mark_failed({'error': 'Paystack secret not configured'})
            return redirect(f"{settings.FRONTEND_URL}/wallet?status=failed")

        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {'Authorization': f'Bearer {paystack_secret}'}

        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            result = resp.json()
        except requests.exceptions.RequestException as e:
            payment.mark_failed({'error': str(e)})
            return redirect(f"{settings.FRONTEND_URL}/wallet?status=failed")

        if not result.get('status'):
            payment.mark_failed(result)
            return redirect(f"{settings.FRONTEND_URL}/wallet?status=failed")

        data = result['data']
        if data['status'] == 'success':
            # ✅ Manually update payment – bypass model method
            payment.status = Payment.PaymentStatus.SUCCESS
            payment.gateway_reference = data['reference']
            payment.gateway_response = data
            payment.paid_at = timezone.now()
            payment.save()

            # Credit wallet (no booking)
            wallet, created = Wallet.objects.get_or_create(
                user=payment.user,
                defaults={
                    'balance': 0.00,
                    'currency': payment.currency,
                    'total_earned': 0.00,
                    'total_withdrawn': 0.00,
                }
            )
            wallet.balance += payment.amount
            wallet.total_earned += payment.amount
            wallet.save()

            return redirect(f"{settings.FRONTEND_URL}/wallet?status=success")
        else:
            payment.mark_failed(data)
            return redirect(f"{settings.FRONTEND_URL}/wallet?status=failed")

    # ─── Webhook (asynchronous) ──────────────────────────────

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def webhook(self, request):
        """
        Webhook endpoint for payment gateway callbacks.
        Should be publicly accessible (no auth).
        """
        serializer = PaymentWebhookSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        transaction_ref = data['transaction_reference']
        gateway_ref = data['gateway_reference']
        status_val = data['status']
        gateway_response = data.get('gateway_response', {})

        payment = get_object_or_404(Payment, transaction_reference=transaction_ref)

        if status_val == Payment.PaymentStatus.SUCCESS:
            # ✅ Manual update – bypass model method
            payment.status = Payment.PaymentStatus.SUCCESS
            payment.gateway_reference = gateway_ref or gateway_response.get('reference', '')
            payment.gateway_response = gateway_response
            payment.paid_at = timezone.now()
            payment.save()

            # Credit wallet (no booking)
            wallet, created = Wallet.objects.get_or_create(
                user=payment.user,
                defaults={
                    'balance': 0.00,
                    'currency': payment.currency,
                    'total_earned': 0.00,
                    'total_withdrawn': 0.00,
                }
            )
            wallet.balance += payment.amount
            wallet.total_earned += payment.amount
            wallet.save()

        elif status_val == Payment.PaymentStatus.FAILED:
            payment.mark_failed(gateway_response)
        else:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'processed'})

    # ─── Refund ───────────────────────────────────────────────

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def refund(self, request, pk=None):
        """
        Refund a payment (full or partial).
        Admin or the payment owner can request a refund.
        """
        payment = self.get_object()

        # Allow admin or the user who made the payment
        if not (request.user.is_staff or payment.user == request.user):
            return Response(
                {'error': 'Only the payment owner or admin can request a refund.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PaymentRefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data.get('amount')
        reason = serializer.validated_data.get('reason', '')

        try:
            refund_amount = payment.refund(amount, reason)
            return Response({
                'status': 'refunded',
                'refunded_amount': refund_amount,
                'remaining_balance': payment.refund_balance,
                'payment': PaymentSerializer(payment).data
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ─── Current User Payments ──────────────────────────────

    @action(detail=False, methods=['get'])
    def my_payments(self, request):
        payments = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

    # ─── Booking Payments (temporarily disabled) ─────────────

    @action(detail=False, methods=['get'])
    def booking_payments(self, request):
        """
        Booking payments are temporarily disabled.
        """
        return Response(
            {'error': 'Booking payments are currently disabled.'},
            status=status.HTTP_400_BAD_REQUEST
        )
