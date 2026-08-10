from rest_framework import serializers
from .models import JobCategory, Job, JobApplication, SavedJob
from companies.serializers import CompanySerializer
from accounts.serializers import UserSerializer


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ('id', 'name', 'slug', 'description', 'icon', 'is_active')


class JobSerializer(serializers.ModelSerializer):
    company_detail = CompanySerializer(source='company', read_only=True)
    posted_by_detail = UserSerializer(source='posted_by', read_only=True)
    category_detail = JobCategorySerializer(source='category', read_only=True)
    applications_count = serializers.IntegerField(read_only=True)
    job_type_display = serializers.CharField(source='get_job_type_display', read_only=True)
    experience_display = serializers.CharField(source='get_experience_level_display', read_only=True)

    class Meta:
        model = Job
        fields = (
            'id', 'company', 'company_detail', 'category', 'category_detail',
            'posted_by', 'posted_by_detail', 'title', 'slug', 'description',
            'requirements', 'responsibilities', 'job_type', 'job_type_display',
            'experience_level', 'experience_display', 'location', 'is_remote',
            'address', 'latitude', 'longitude', 'salary_min', 'salary_max',
            'salary_currency', 'is_salary_negotiable', 'benefits',
            'application_deadline', 'posted_at', 'updated_at', 'status',
            'views', 'applications_count', 'is_featured', 'is_urgent',
            'created_at', 'updated_at'
        )
        read_only_fields = ('slug', 'posted_at', 'updated_at', 'views', 'applications_count')


class JobListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Job
        fields = (
            'id', 'title', 'slug', 'company_name', 'category_name', 'location',
            'is_remote', 'job_type', 'salary_min', 'salary_max', 'status',
            'is_featured', 'is_urgent', 'views', 'applications_count', 'created_at'
        )


class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            'company', 'category', 'title', 'description', 'requirements',
            'responsibilities', 'job_type', 'experience_level', 'location',
            'is_remote', 'address', 'latitude', 'longitude', 'salary_min',
            'salary_max', 'salary_currency', 'is_salary_negotiable',
            'benefits', 'application_deadline', 'is_featured', 'is_urgent'
        )


class JobApplicationSerializer(serializers.ModelSerializer):
    candidate_detail = UserSerializer(source='candidate', read_only=True)
    job_detail = JobListSerializer(source='job', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = JobApplication
        fields = (
            'id', 'job', 'job_detail', 'candidate', 'candidate_detail',
            'cover_letter', 'resume', 'status', 'status_display', 'reviewed_at',
            'notes', 'match_score', 'created_at', 'updated_at'
        )
        read_only_fields = ('candidate', 'created_at', 'updated_at')


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ('cover_letter', 'resume')


class SavedJobSerializer(serializers.ModelSerializer):
    job_detail = JobListSerializer(source='job', read_only=True)

    class Meta:
        model = SavedJob
        fields = ('id', 'job', 'job_detail', 'user', 'created_at')
        read_only_fields = ('user', 'created_at')