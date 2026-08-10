import uuid
from decimal import Decimal
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Wallet, WalletTransaction
from .serializers import (
    WalletSerializer,
    WalletListSerializer,
    WalletCreditSerializer,
    WalletDebitSerializer,
    WalletTransactionSerializer,
)


class WalletViewSet(viewsets.ModelViewSet):
    """
    API endpoint for wallets.
    """
    queryset = Wallet.objects.select_related('user').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'is_active']
    search_fields = ['user__email']
    ordering_fields = ['balance', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return WalletListSerializer
        return WalletSerializer

    def perform_create(self, serializer):
        # Only allow creation if user doesn't have a wallet yet
        if Wallet.objects.filter(user=self.request.user).exists():
            raise serializers.ValidationError("User already has a wallet.")
        serializer.save(user=self.request.user)

    # ─── Custom Actions ──────────────────────────────────────

    @action(detail=False, methods=['get'])
    def my_wallet(self, request):
        """
        Get the current user's wallet – creates one if it doesn't exist.
        """
        wallet, created = Wallet.objects.get_or_create(
            user=request.user,
            defaults={
                'balance': 0.00,
                'currency': 'GHS',
                'total_earned': 0.00,
                'total_withdrawn': 0.00,
            }
        )
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def credit(self, request):
        """
        Credit the current user's wallet (admin only).
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admin can credit wallets.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = WalletCreditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet = get_object_or_404(Wallet, user=request.user)
        try:
            transaction = wallet.credit(
                amount=serializer.validated_data['amount'],
                description=serializer.validated_data['description'],
                metadata=serializer.validated_data.get('metadata', {})
            )
            return Response(WalletTransactionSerializer(transaction).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def debit(self, request):
        """
        Debit the current user's wallet (admin only).
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admin can debit wallets.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = WalletDebitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet = get_object_or_404(Wallet, user=request.user)
        try:
            transaction = wallet.debit(
                amount=serializer.validated_data['amount'],
                description=serializer.validated_data['description'],
                metadata=serializer.validated_data.get('metadata', {})
            )
            return Response(WalletTransactionSerializer(transaction).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def transactions(self, request):
        """
        Get transactions for the current user's wallet – creates a wallet if missing.
        """
        wallet, created = Wallet.objects.get_or_create(
            user=request.user,
            defaults={
                'balance': 0.00,
                'currency': 'GHS',
                'total_earned': 0.00,
                'total_withdrawn': 0.00,
            }
        )
        transactions = wallet.transactions.all()
        serializer = WalletTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    # ─── Withdraw (Artisans only) ─────────────────────────────

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def withdraw(self, request):
        """
        Request a withdrawal from the wallet (artisans only).
        Creates a pending debit transaction that must be approved by admin.
        Also creates a wallet if the user doesn't have one.
        """
        # Only artisans can withdraw
        if not hasattr(request.user, 'artisan_profile'):
            return Response(
                {'error': 'Only artisans can withdraw.'},
                status=status.HTTP_403_FORBIDDEN
            )

        amount = request.data.get('amount')
        if not amount:
            return Response(
                {'error': 'Amount is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = Decimal(str(amount))
        except Exception:
            return Response(
                {'error': 'Invalid amount.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if amount <= 0:
            return Response(
                {'error': 'Amount must be positive.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Lazy create wallet if it doesn't exist
        wallet, created = Wallet.objects.get_or_create(
            user=request.user,
            defaults={
                'balance': 0.00,
                'currency': 'GHS',
                'total_earned': 0.00,
                'total_withdrawn': 0.00,
            }
        )

        if amount > wallet.balance:
            return Response(
                {'error': 'Insufficient balance.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a pending withdrawal transaction
        transaction = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type=WalletTransaction.TransactionType.DEBIT,
            amount=amount,
            description=f'Withdrawal request by {request.user.email}',
            reference=f'WD-{uuid.uuid4().hex[:8].upper()}',
            balance_after=wallet.balance,  # not yet deducted
            status=WalletTransaction.TransactionStatus.PENDING,
            metadata={
                'requested_by': request.user.id,
                'admin_approved': False
            }
        )

        return Response({
            'status': 'withdrawal_requested',
            'transaction': WalletTransactionSerializer(transaction).data,
            'message': 'Withdrawal request submitted. You will be notified once approved.'
        }, status=status.HTTP_201_CREATED)

    # ─── Approve Withdrawal (Admin only) ──────────────────────

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve_withdrawal(self, request, pk=None):
        """
        Approve a pending withdrawal transaction for a specific wallet.
        Expects `transaction_id` in the request body.
        """
        transaction_id = request.data.get('transaction_id')
        if not transaction_id:
            return Response(
                {'error': 'transaction_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            transaction = WalletTransaction.objects.get(
                id=transaction_id,
                wallet_id=pk
            )
        except WalletTransaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found for this wallet.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if transaction.transaction_type != WalletTransaction.TransactionType.DEBIT:
            return Response(
                {'error': 'Only debit transactions can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if transaction.status != WalletTransaction.TransactionStatus.PENDING:
            return Response(
                {'error': 'Transaction already processed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        wallet = transaction.wallet
        if transaction.amount > wallet.balance:
            return Response(
                {'error': 'Insufficient balance.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Deduct balance
        wallet.balance -= transaction.amount
        wallet.total_withdrawn += transaction.amount
        wallet.last_transaction_at = timezone.now()
        wallet.save()

        # Mark transaction as completed
        transaction.status = WalletTransaction.TransactionStatus.COMPLETED
        transaction.processed_at = timezone.now()
        transaction.balance_after = wallet.balance
        transaction.save()

        # Create notification for the user
        try:
            from notifications.models import Notification
            Notification.create_notification(
                user=wallet.user,
                title='Withdrawal Approved',
                message=f'Your withdrawal of {wallet.currency} {transaction.amount} has been approved.',
                notification_type=Notification.Type.WALLET,
                metadata={'transaction_id': transaction.id}
            )
        except ImportError:
            # If notifications app is not installed, silently skip
            pass

        return Response({
            'status': 'approved',
            'transaction': WalletTransactionSerializer(transaction).data,
            'message': 'Withdrawal approved successfully.'
        })
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def pending_withdrawals(self, request):
        """
        List all pending withdrawal transactions (admin only).
        """
        transactions = WalletTransaction.objects.filter(
            transaction_type=WalletTransaction.TransactionType.DEBIT,
            status=WalletTransaction.TransactionStatus.PENDING
        ).select_related('wallet__user')
        serializer = WalletTransactionSerializer(transactions, many=True)
        return Response(serializer.data)    
