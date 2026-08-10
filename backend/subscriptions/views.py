from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import SubscriptionPlan, Subscription
from .serializers import (
    SubscriptionPlanSerializer,
    SubscriptionPlanListSerializer,
    SubscriptionSerializer,
    SubscriptionListSerializer,
    SubscriptionActivateSerializer,
    SubscriptionRenewSerializer,
)


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    """
    API endpoint for subscription plans.
    """
    queryset = SubscriptionPlan.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'billing_cycle']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'duration_days', 'created_at']
    ordering = ['price']

    def get_serializer_class(self):
        if self.action == 'list':
            return SubscriptionPlanListSerializer
        return SubscriptionPlanSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise permissions.PermissionDenied("Only admins can create subscription plans.")
        serializer.save()


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user subscriptions.
    """
    queryset = Subscription.objects.select_related('user', 'plan').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'plan', 'status', 'auto_renew']
    search_fields = ['subscription_reference', 'user__email', 'plan__name']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return SubscriptionListSerializer
        return SubscriptionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ─── Custom Actions ──────────────────────────────────────

    @action(detail=False, methods=['post'])
    def activate(self, request):
        """
        Activate a new subscription for the current user.
        """
        serializer = SubscriptionActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan = get_object_or_404(SubscriptionPlan, id=serializer.validated_data['plan_id'])
        payment_ref = serializer.validated_data.get('payment_reference', '')
        auto_renew = serializer.validated_data.get('auto_renew', True)

        # Check if user already has an active subscription
        existing = Subscription.objects.filter(
            user=request.user,
            status__in=[Subscription.Status.ACTIVE, Subscription.Status.TRIAL]
        ).first()
        if existing:
            return Response({
                'error': 'You already have an active subscription.',
                'subscription': SubscriptionSerializer(existing).data
            }, status=status.HTTP_400_BAD_REQUEST)

        # Calculate dates
        start_date = timezone.now().date()
        end_date = start_date + timezone.timedelta(days=plan.duration_days)
        trial_end_date = None
        if plan.trial_days > 0:
            trial_end_date = start_date + timezone.timedelta(days=plan.trial_days)

        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            trial_end_date=trial_end_date,
            status=Subscription.Status.TRIAL if trial_end_date else Subscription.Status.ACTIVE,
            auto_renew=auto_renew,
            gateway_reference=payment_ref
        )

        return Response({
            'subscription': SubscriptionSerializer(subscription).data,
            'message': 'Subscription activated successfully.'
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """
        Renew a subscription.
        """
        subscription = self.get_object()

        # Check permission: user must be the subscriber or admin
        if subscription.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You are not authorized to renew this subscription.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SubscriptionRenewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment_ref = serializer.validated_data.get('payment_reference', '')

        try:
            subscription.renew(gateway_ref=payment_ref)
            return Response({
                'subscription': SubscriptionSerializer(subscription).data,
                'message': 'Subscription renewed successfully.'
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a subscription.
        """
        subscription = self.get_object()

        if subscription.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You are not authorized to cancel this subscription.'},
                status=status.HTTP_403_FORBIDDEN
            )

        reason = request.data.get('reason', '')
        try:
            subscription.cancel(reason)
            return Response({
                'subscription': SubscriptionSerializer(subscription).data,
                'message': 'Subscription cancelled successfully.'
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def toggle_auto_renew(self, request, pk=None):
        """
        Toggle auto-renewal for a subscription.
        """
        subscription = self.get_object()

        if subscription.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You are not authorized to modify this subscription.'},
                status=status.HTTP_403_FORBIDDEN
            )

        subscription.toggle_auto_renew()
        return Response({
            'subscription': SubscriptionSerializer(subscription).data,
            'message': f'Auto-renewal {"enabled" if subscription.auto_renew else "disabled"} successfully.'
        })

    @action(detail=False, methods=['get'])
    def my_subscription(self, request):
        """
        Get the current user's active subscription.
        """
        subscription = Subscription.objects.filter(
            user=request.user,
            status__in=[Subscription.Status.ACTIVE, Subscription.Status.TRIAL]
        ).first()

        if not subscription:
            return Response({
                'has_subscription': False,
                'message': 'No active subscription found.'
            })

        serializer = self.get_serializer(subscription)
        return Response({
            'has_subscription': True,
            'subscription': serializer.data
        })

    @action(detail=False, methods=['get'])
    def my_subscriptions(self, request):
        """
        Get all subscriptions for the current user.
        """
        subscriptions = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)
