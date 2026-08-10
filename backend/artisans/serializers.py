# artisan/serializers.py
from rest_framework import serializers
from .models import ArtisanProfile, Skill, ArtisanAvailability
from accounts.serializers import UserListSerializer

# ─── Import the models for querysets ──────────────────────
from incident_category.models import IncidentCategory, SubCategory

# ─── Import serializers for nested objects ─────────────────
from incident_category.serializers import (
    IncidentCategorySerializer,
    SubCategorySerializer,
)


class SkillSerializer(serializers.ModelSerializer):
    """Legacy skill serializer."""
    class Meta:
        model = Skill
        fields = ['id', 'name', 'description', 'is_active']
        read_only_fields = ['id']


class ArtisanAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtisanAvailability
        fields = ['id', 'day_of_week', 'start_time', 'end_time', 'is_working']
        read_only_fields = ['id']


class ArtisanProfileListSerializer(serializers.ModelSerializer):
    user_detail = UserListSerializer(source='user', read_only=True)

    # ─── New: category (IncidentCategory) ────────────────────
    category_detail = IncidentCategorySerializer(source='category', read_only=True)

    # ─── New: skills (SubCategory) ──────────────────────────
    skills = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # list of IDs
    skills_detail = SubCategorySerializer(source='skills', many=True, read_only=True)  # full objects

    # ─── Legacy skills (old Skill model) ─────────────────────
    legacy_skills = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    legacy_skills_detail = SkillSerializer(source='legacy_skills', many=True, read_only=True)

    current_workload = serializers.ReadOnlyField()
    can_take_more = serializers.ReadOnlyField()

    class Meta:
        model = ArtisanProfile
        fields = [
            'id', 'user', 'user_detail',
            'category', 'category_detail',
            'skills', 'skills_detail',          # new SubCategory skills
            'legacy_skills', 'legacy_skills_detail',  # old Skill model
            'is_available', 'current_location_lat', 'current_location_lng',
            'max_concurrent_jobs', 'average_rating', 'current_workload', 'can_take_more',
            'hire_date', 'bio'
        ]
        read_only_fields = ['id', 'average_rating']


class ArtisanProfileDetailSerializer(serializers.ModelSerializer):
    user_detail = UserListSerializer(source='user', read_only=True)
    availability = ArtisanAvailabilitySerializer(many=True, read_only=True)

    # ─── New fields ──────────────────────────────────────────
    category_detail = IncidentCategorySerializer(source='category', read_only=True)
    skills = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    skills_detail = SubCategorySerializer(source='skills', many=True, read_only=True)

    # ─── Legacy ──────────────────────────────────────────────
    legacy_skills = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    legacy_skills_detail = SkillSerializer(source='legacy_skills', many=True, read_only=True)

    current_workload = serializers.ReadOnlyField()
    can_take_more = serializers.ReadOnlyField()

    class Meta:
        model = ArtisanProfile
        fields = '__all__'
        read_only_fields = ['id', 'user', 'average_rating', 'current_workload', 'can_take_more']


class ArtisanProfileCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating artisan profiles.
    Accepts category ID and skills IDs.
    """
    category = serializers.PrimaryKeyRelatedField(
        queryset=IncidentCategory.objects.filter(is_active=True),
        required=False,
        allow_null=True
    )
    skills = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=SubCategory.objects.filter(is_active=True),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = ArtisanProfile
        fields = [
            'category', 'skills', 'is_available',
            'current_location_lat', 'current_location_lng',
            'max_concurrent_jobs', 'hire_date', 'bio'
        ]

    def create(self, validated_data):
        skills = validated_data.pop('skills', [])
        instance = super().create(validated_data)
        instance.skills.set(skills)
        return instance

    def update(self, instance, validated_data):
        skills = validated_data.pop('skills', None)
        instance = super().update(instance, validated_data)
        if skills is not None:
            instance.skills.set(skills)
        return instance


class ArtisanAvailabilityCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtisanAvailability
        fields = ['day_of_week', 'start_time', 'end_time', 'is_working']


# ─── Aliases for backward compatibility ──────────────────────
ArtisanListSerializer = ArtisanProfileListSerializer
ArtisanSerializer = ArtisanProfileDetailSerializer   