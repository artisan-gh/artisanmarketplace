# accounts/serializers.py
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from .models import User, LoginHistory, UserSession

# 👇 Import your ArtisanProfile model (adjust the import path to your app)
from artisans.models import ArtisanProfile  # Change 'artisans' to your actual app name
from incident_category.models import IncidentCategory


# ------------------------------------------------------------
# 1. LOGIN SERIALIZER (Extends Simple JWT)
# ------------------------------------------------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends JWT login to:
    - Check if user can_login (active, not deleted, account_status=ACTIVE)
    - Return user profile data along with tokens.
    - Log successful/failed attempts.
    """
    # ✅ TELL SIMPLE JWT TO USE EMAIL AS THE USERNAME FIELD
    username_field = "email"

    def validate(self, attrs):
        email = attrs.get("email", "").lower()
        password = attrs.get("password", "")

        # Authenticate using email
        user = authenticate(request=self.context.get("request"), email=email, password=password)

        if not user:
            # Log failed attempt (if we have the request object)
            request = self.context.get("request")
            ip = request.META.get("REMOTE_ADDR") if request else None
            ua = request.META.get("HTTP_USER_AGENT") if request else ""

            LoginHistory.objects.create(
                user=None,  # No user found
                ip_address=ip,
                user_agent=ua,
                successful=False,
                failure_reason="Invalid email or password"
            )
            raise AuthenticationFailed("Invalid email or password.")

        # Check if user is allowed to login
        if not user.can_login:
            reason = "Account is locked, suspended, or deleted."
            if user.is_deleted:
                reason = "This account has been deleted."
            elif user.account_status == User.AccountStatus.SUSPENDED:
                reason = "Account is suspended. Please contact support."
            elif user.account_status == User.AccountStatus.LOCKED:
                reason = "Account is locked due to security reasons."
            elif user.account_status == User.AccountStatus.PENDING:
                reason = "Account is pending KYC verification."

            # Log failed attempt
            request = self.context.get("request")
            LoginHistory.objects.create(
                user=user,
                ip_address=request.META.get("REMOTE_ADDR") if request else None,
                user_agent=request.META.get("HTTP_USER_AGENT", "") if request else "",
                successful=False,
                failure_reason=reason
            )
            raise AuthenticationFailed(reason)

        # ✅ Now call parent's validate – it will use attrs["email"] because of username_field
        data = super().validate(attrs)

        # Log successful login
        request = self.context.get("request")
        LoginHistory.objects.create(
            user=user,
            ip_address=request.META.get("REMOTE_ADDR") if request else None,
            user_agent=request.META.get("HTTP_USER_AGENT") if request else "",
            successful=True,
            device_name=request.META.get("HTTP_SEC_CH_UA_PLATFORM", "") if request else "",
            browser=request.META.get("HTTP_SEC_CH_UA", "") if request else "",
        )

        # Update user's online status and last login IP
        user.is_online = True
        user.last_seen = timezone.now()
        if request:
            user.last_login_ip = request.META.get("REMOTE_ADDR")
        user.save(update_fields=["is_online", "last_seen", "last_login_ip"])

        # Create refresh token and store session metadata
        refresh = RefreshToken.for_user(user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        jti = refresh.get("jti")  # SimpleJWT includes 'jti' claim
        expires_at = timezone.now() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]

        UserSession.objects.create(
            user=user,
            jti=jti,
            device_name=request.META.get("HTTP_SEC_CH_UA_PLATFORM", "") if request else "",
            ip_address=request.META.get("REMOTE_ADDR") if request else None,
            user_agent=request.META.get("HTTP_USER_AGENT", "") if request else "",
            browser=request.META.get("HTTP_SEC_CH_UA", "") if request else "",
            operating_system=request.META.get("HTTP_SEC_CH_UA_PLATFORM_VERSION", "") if request else "",
            expires_at=expires_at,
        )

        # Add user data to response
        data["user"] = UserDetailSerializer(user, context=self.context).data
        data["user_type"] = user.user_type  # For frontend routing

        return data


# ------------------------------------------------------------
# 2. USER BASE SERIALIZER (List view - minimal fields)
# ------------------------------------------------------------
class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "first_name",
            "last_name",
            "user_type",
            "user_type_display",
            "account_status",
            "is_active",
            "is_verified",
            "is_deleted",
            "employee_number",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_full_name(self, obj):
        return obj.get_full_name()


# ------------------------------------------------------------
# 3. USER DETAIL SERIALIZER (Profile view - all fields)
# ------------------------------------------------------------
class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    can_login = serializers.ReadOnlyField()
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    account_status_display = serializers.CharField(source='get_account_status_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)

    class Meta:
        model = User
        fields = [
            # IDs & names
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            # Role
            "user_type",
            "user_type_display",
            # Employee
            "employee_number",
            "department",
            "job_title",
            "hire_date",
            # Profile
            "profile_picture",
            "date_of_birth",
            "gender",
            "gender_display",
            # KYC
            "identification_document_type",
            "identification_number",
            "proof_of_address",
            "is_verified",
            "email_verified",
            "phone_verified",
            # Account
            "account_status",
            "account_status_display",
            "is_active",
            "is_deleted",
            "can_login",
            # Online
            "is_online",
            "last_seen",
            "last_login_ip",
            # Emergency
            "emergency_contact_name",
            "emergency_contact_phone",
            # Timezone
            "timezone",
            # Timestamps
            "created_at",
            "updated_at",
            # New profile fields
            "introduction",
            "nationality",
            "education",
            "interests",
            "languages",
            "employer",
            # Social links
            "whatsapp",
            "facebook",
            "instagram",
            "twitter",
        ]
        read_only_fields = [
            "id",
            "is_online",
            "last_seen",
            "last_login_ip",
            "created_at",
            "updated_at",
            "can_login",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()


# ------------------------------------------------------------
# 4. USER CREATE SERIALIZER (Staff/HR creates new user)
# ------------------------------------------------------------
class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "phone_number",
            "user_type",
            "employee_number",
            "department",
            "job_title",
            "hire_date",
            "date_of_birth",
            "gender",
            "identification_document_type",
            "identification_number",
            "account_status",
            "timezone",
            "emergency_contact_name",
            "emergency_contact_phone",
        ]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        employee_number = data.get("employee_number")
        if employee_number and User.objects.filter(employee_number=employee_number).exists():
            raise serializers.ValidationError({"employee_number": "This employee number already exists."})

        data["email"] = data["email"].lower()
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password", None)

        if not validated_data.get("employee_number"):
            last_emp = User.objects.filter(employee_number__isnull=False).order_by("-id").first()
            if last_emp and last_emp.employee_number:
                try:
                    num = int(last_emp.employee_number.split("-")[-1]) + 1
                    validated_data["employee_number"] = f"EMP-{timezone.now().year}-{num:06d}"
                except (ValueError, IndexError):
                    validated_data["employee_number"] = f"EMP-{timezone.now().year}-000001"
            else:
                validated_data["employee_number"] = f"EMP-{timezone.now().year}-000001"

        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)

        # Set is_active based on account_status
        user.is_active = (user.account_status == User.AccountStatus.ACTIVE)
        user.save()
        return user


# ------------------------------------------------------------
# 5. USER UPDATE SERIALIZER (Edit profile)
# ------------------------------------------------------------
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "profile_picture",
            "date_of_birth",
            "gender",
            "identification_document_type",
            "identification_number",
            "proof_of_address",
            "department",
            "job_title",
            "timezone",
            "emergency_contact_name",
            "emergency_contact_phone",
        ]

    def update(self, instance, validated_data):
        if "first_name" in validated_data:
            validated_data["first_name"] = validated_data["first_name"].title()
        if "last_name" in validated_data:
            validated_data["last_name"] = validated_data["last_name"].title()
        return super().update(instance, validated_data)


# ------------------------------------------------------------
# 6. ADMIN USER STATUS UPDATE (Only status/role changes)
# ------------------------------------------------------------
class UserStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "user_type",
            "account_status",
            "is_active",
            "is_verified",
            "is_deleted",
            "is_online",
        ]

    def validate(self, data):
        if "account_status" in data:
            data["is_active"] = (data["account_status"] == User.AccountStatus.ACTIVE)
        return data


# ------------------------------------------------------------
# 7. CHANGE PASSWORD SERIALIZER
# ------------------------------------------------------------
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError({"confirm_new_password": "Passwords do not match."})
        return data


# ------------------------------------------------------------
# 8. LOGIN HISTORY SERIALIZER
# ------------------------------------------------------------
class LoginHistorySerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    successful_display = serializers.CharField(source='get_successful_display', read_only=True)

    class Meta:
        model = LoginHistory
        fields = [
            "id",
            "user_email",
            "ip_address",
            "device_name",
            "browser",
            "operating_system",
            "successful",
            "successful_display",
            "failure_reason",
            "logout_time",
            "created_at",
        ]
        read_only_fields = "__all__"

    def get_user_email(self, obj):
        return obj.user.email if obj.user else "Unknown"


# ------------------------------------------------------------
# 9. USER SESSION SERIALIZER
# ------------------------------------------------------------
class UserSessionSerializer(serializers.ModelSerializer):
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = UserSession
        fields = [
            "id",
            "device_name",
            "ip_address",
            "browser",
            "operating_system",
            "created_at",
            "last_activity",
            "expires_at",
            "revoked",
            "revoked_at",
            "is_expired",
        ]
        read_only_fields = "__all__"


# ------------------------------------------------------------
# 10. USER REGISTER SERIALIZER (Public self-registration)
# ------------------------------------------------------------
class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True,
        error_messages={'required': 'Email is required.'}
    )
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    confirm_password = serializers.CharField(write_only=True, min_length=8, required=True)

    # ─── Additional artisan fields (not on User model) ───
    availability_days = serializers.JSONField(
        required=True,
        error_messages={'required': 'Please select at least one availability day.'}
    )
    skills = serializers.JSONField(
        required=True,
        error_messages={'required': 'Please select at least one skill.'}
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=IncidentCategory.objects.all(),
        required=True,
        error_messages={
            'required': 'Please select a category.',
            'does_not_exist': 'Selected category does not exist.',
            'incorrect_type': 'Category must be a valid category ID.',
        }
    )

    # ─── File fields (on User model) ───
    profile_picture = serializers.ImageField(
        required=True,
        error_messages={'required': 'Profile picture is required.'}
    )
    # ✅ Changed from ImageField to FileField to accept PDFs as well
    proof_of_address = serializers.FileField(
        required=True,
        error_messages={'required': 'ID document upload is required.'}
    )

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "phone_number",
            "user_type",
            "date_of_birth",
            "gender",
            "identification_document_type",
            "identification_number",
            "timezone",
            "emergency_contact_name",
            "emergency_contact_phone",
            # ─── Added fields ───
            "profile_picture",
            "proof_of_address",
            "availability_days",
            "skills",
            "category",
        ]
        extra_kwargs = {
            "user_type": {"required": True, "error_messages": {"required": "User type is required."}},
            "first_name": {"required": True, "error_messages": {"required": "First name is required."}},
            "last_name": {"required": True, "error_messages": {"required": "Last name is required."}},
            "phone_number": {"required": True, "error_messages": {"required": "Phone number is required."}},
            "date_of_birth": {"required": True, "error_messages": {"required": "Date of birth is required."}},
            "gender": {"required": True, "error_messages": {"required": "Gender is required."}},
            "identification_document_type": {"required": True, "error_messages": {"required": "ID document type is required."}},
            "identification_number": {"required": True, "error_messages": {"required": "ID number is required."}},
            "timezone": {"required": True, "error_messages": {"required": "Timezone is required."}},
            "emergency_contact_name": {"required": True, "error_messages": {"required": "Emergency contact name is required."}},
            "emergency_contact_phone": {"required": True, "error_messages": {"required": "Emergency contact phone is required."}},
        }

    def validate(self, data):
        # 1. Check passwords match
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        # 2. Normalize email
        data["email"] = data["email"].lower()

        # 3. Validate that availability_days is not an empty list
        if not data.get("availability_days") or len(data["availability_days"]) == 0:
            raise serializers.ValidationError({"availability_days": "At least one availability day must be selected."})

        # 4. Validate that skills is not an empty list
        if not data.get("skills") or len(data["skills"]) == 0:
            raise serializers.ValidationError({"skills": "At least one skill must be selected."})

        return data

    def create(self, validated_data):
        # Remove confirmation password
        validated_data.pop("confirm_password", None)

        # Pop artisan-specific fields that are NOT on the User model
        # (they will be handled by the view)
        validated_data.pop("availability_days", None)
        validated_data.pop("skills", None)
        validated_data.pop("category", None)

        # New accounts require approval
        validated_data["account_status"] = User.AccountStatus.PENDING
        validated_data["is_active"] = False

        # Generate unique employee number
        year = timezone.now().year
        last_employee = (
            User.objects
            .filter(employee_number__startswith=f"EMP-{year}-")
            .order_by("-id")
            .first()
        )

        if last_employee:
            try:
                last_number = int(last_employee.employee_number.split("-")[-1])
                next_number = last_number + 1
            except (ValueError, AttributeError):
                next_number = 1
        else:
            next_number = 1

        while True:
            employee_number = f"EMP-{year}-{next_number:06d}"
            if not User.objects.filter(employee_number=employee_number).exists():
                break
            next_number += 1

        validated_data["employee_number"] = employee_number

        # Create user
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # ─── ArtisanProfile is NOT created here – the view will handle it ───

        return user


# ------------------------------------------------------------
# 11. ALIAS FOR BACKWARD COMPATIBILITY
# ------------------------------------------------------------
UserSerializer = UserDetailSerializer