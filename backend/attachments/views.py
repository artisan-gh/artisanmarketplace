from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Attachment
from .serializers import AttachmentListSerializer, AttachmentCreateUpdateSerializer
from accounts.permissions import IsAdminOrStaff

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['incident']

    def get_serializer_class(self):
        if self.action == 'list':
            return AttachmentListSerializer
        return AttachmentCreateUpdateSerializer

    def perform_create(self, serializer):
        # Auto-set uploaded_by
        serializer.save(uploaded_by=self.request.user)
