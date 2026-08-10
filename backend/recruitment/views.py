from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils import timezone
from .models import JobCategory, Job, JobApplication, SavedJob
from .serializers import (
    JobCategorySerializer, JobSerializer, JobListSerializer,
    JobCreateSerializer, JobApplicationSerializer,
    JobApplicationCreateSerializer, SavedJobSerializer
)


class JobCategoryViewSet(viewsets.ModelViewSet):
    queryset = JobCategory.objects.filter(is_active=True).all()
    serializer_class = JobCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.select_related('company', 'category', 'posted_by').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'job_type', 'experience_level', 'status', 'is_remote', 'is_featured']
    search_fields = ['title', 'description', 'requirements', 'responsibilities', 'location']
    ordering_fields = ['salary_min', 'created_at', 'views']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(status=Job.Status.OPEN)

    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        if self.action == 'create':
            return JobCreateSerializer
        return JobSerializer

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        job = self.get_object()
        if job.status != Job.Status.OPEN:
            return Response({'error': 'Job is not open for applications.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = JobApplicationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application, created = JobApplication.objects.get_or_create(
            job=job,
            candidate=request.user,
            defaults=serializer.validated_data
        )
        if created:
            job.applications_count += 1
            job.save()
            return Response({'status': 'applied'})
        return Response({'error': 'Already applied.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def save_job(self, request, pk=None):
        job = self.get_object()
        saved, created = SavedJob.objects.get_or_create(job=job, user=request.user)
        if created:
            return Response({'status': 'saved'})
        return Response({'status': 'already_saved'})

    @action(detail=True, methods=['post'])
    def unsave_job(self, request, pk=None):
        job = self.get_object()
        SavedJob.objects.filter(job=job, user=request.user).delete()
        return Response({'status': 'unsaved'})

    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        job = self.get_object()
        job.views += 1
        job.save()
        return Response({'views': job.views})

    @action(detail=False, methods=['get'])
    def my_jobs(self, request):
        qs = self.get_queryset().filter(posted_by=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.select_related('job', 'candidate').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'job']
    ordering_fields = ['created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        # Candidates see their own applications; employers see applications for their jobs
        return self.queryset.filter(
            models.Q(candidate=user) | models.Q(job__company__members__user=user)
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'create':
            return JobApplicationCreateSerializer
        return JobApplicationSerializer

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        application = self.get_object()
        status_val = request.data.get('status')
        if not status_val:
            return Response({'error': 'status is required'}, status=status.HTTP_400_BAD_REQUEST)
        application.status = status_val
        application.reviewed_at = timezone.now()
        application.save()
        return Response({'status': 'updated'})

    @action(detail=False, methods=['get'])
    def my_applications(self, request):
        qs = self.get_queryset().filter(candidate=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class SavedJobViewSet(viewsets.ModelViewSet):
    queryset = SavedJob.objects.select_related('job', 'user').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        return SavedJobSerializer
