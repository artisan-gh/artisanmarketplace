# accounts/models.py
import uuid
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.utils import timezone
from django.conf import settings


# ─── Employee Sequence (thread‑safe counter per year) ──────
class EmployeeSequence(models.Model):
    """
    Thread‑safe sequence for generating unique employee numbers per year.
    """
    year = models.PositiveIntegerField(unique=True)
    current_number = models.PositiveIntegerField(default=0)

    @classmethod
    def get_next_number(cls, year):
        with transaction.atomic():
            seq, _ = cls.objects.select_for_update().get_or_create(year=year)
            seq.current_number += 1
            seq.save()
            return seq.current_number

    class Meta:
        verbose_name_plural = "Employee Sequences"


class UserManager(DjangoUserManager):
    """
    Custom user manager that uses email as the unique identifier.
    Inherits Django's built-in UserManager to preserve compatibility.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required.")

        email = self.normalize_email(email)

        # Normalize first/last names (title case)
        if extra_fields.get("first_name"):
            extra_fields["first_name"] = extra_fields["first_name"].title()
        if extra_fields.get("last_name"):
            extra_fields["last_name"] = extra_fields["last_name"].title()

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("account_status", User.AccountStatus.ACTIVE)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model – internal staff only (no external clients).
    Uses email as the login field.
    Authorization is handled via Django Groups & Permissions.
    `user_type` is kept for UI convenience (e.g., dashboard routing).
    """

    class UserType(models.TextChoices):
        COMPANY    = "COMPANY", "Company"         # B2B client admin (portal)
        AGENT      = "AGENT", "Call Center Agent"
        DISPATCHER = "DISPATCHER", "Dispatcher"
        SUPERVISOR = "SUPERVISOR", "Supervisor"
        ARTISAN    = "ARTISAN", "Artisan"
        MANAGER    = "MANAGER", "Manager"
        ADMIN      = "ADMIN", "System Admin"

    class Gender(models.TextChoices):
        MALE   = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        OTHER  = "OTHER", "Other"

    class AccountStatus(models.TextChoices):
        ACTIVE    = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspended"
        LOCKED    = "LOCKED", "Locked"
        PENDING   = "PENDING", "Pending"

    # Use UUID primary key for security
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Remove the default username field
    username = None

    # Basic personal info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    # Email is the unique login field – indexed for fast lookup
    email = models.EmailField(unique=True, db_index=True)

    # Phone – indexed, not necessarily unique
    phone_number = models.CharField(
        max_length=20,
        db_index=True,
        null=True,
        blank=True
    )

    # KYC / Identification
    identification_document_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g., National ID, Passport, Driver's License"
    )
    identification_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_index=True
    )
    proof_of_address = models.FileField(
        upload_to="kyc/",
        blank=True,
        null=True
    )

    # Role convenience (authorization uses Groups/Permissions)
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.AGENT,
        db_index=True
    )

    # Employee information
    employee_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True,
        db_index=True
    )
    department = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField(blank=True, null=True)

    # Additional profile
    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True
    )

    # ─── ✨ NEW: User Profile Fields (for settings page) ──────
    introduction = models.TextField(
        blank=True,
        null=True,
        help_text="A short introduction or bio."
    )
    nationality = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Country of citizenship."
    )
    education = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Highest level of education."
    )
    interests = models.TextField(
        blank=True,
        null=True,
        help_text="Hobbies, interests, or passions."
    )
    languages = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Languages spoken (comma‑separated)."
    )
    employer = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Current employer or organization."
    )

    # ─── ✨ NEW: Social Media Links ────────────────────────────
    whatsapp = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="WhatsApp phone number."
    )
    facebook = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Facebook username or URL."
    )
    instagram = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Instagram username."
    )
    twitter = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Twitter/X handle."
    )

    # ─── End of new fields ─────────────────────────────────────

    # Verification
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    # Account status (finer control)
    account_status = models.CharField(
        max_length=20,
        choices=AccountStatus.choices,
        default=AccountStatus.ACTIVE,
        db_index=True
    )

    # Online presence
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)

    # Last login IP
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    # Emergency contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)

    # Timezone preference
    timezone = models.CharField(max_length=50, default="UTC")

    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Django authentication requirements
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee_number"],
                name="unique_employee_number"
            )
        ]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["employee_number"]),
            models.Index(fields=["user_type"]),
            models.Index(fields=["account_status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["is_deleted"]),
        ]

    def __str__(self):
        return f"{self.get_full_name()} - {self.email}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def save(self, *args, **kwargs):
        # Ensure email is always lowercase
        if self.email:
            self.email = self.email.lower()

        # Generate employee number if not set
        if not self.employee_number:
            year = timezone.now().year
            number = EmployeeSequence.get_next_number(year)
            self.employee_number = f"EMP-{year}-{number:04d}"

        # Convert empty string to None (safety)
        if self.employee_number == '':
            self.employee_number = None

        super().save(*args, **kwargs)

    @property
    def can_login(self):
        """Check if user is allowed to authenticate."""
        return (
            self.is_active
            and not self.is_deleted
            and self.account_status == self.AccountStatus.ACTIVE
        )

    # Convenience properties for UI
    @property
    def is_artisan(self):
        return self.user_type == self.UserType.ARTISAN

    @property
    def is_agent(self):
        return self.user_type == self.UserType.AGENT

    @property
    def is_dispatcher(self):
        return self.user_type == self.UserType.DISPATCHER

    @property
    def is_supervisor(self):
        return self.user_type == self.UserType.SUPERVISOR

    @property
    def is_manager(self):
        return self.user_type == self.UserType.MANAGER

    @property
    def is_admin(self):
        return self.user_type == self.UserType.ADMIN

    def has_group(self, group_name):
        """Check if user belongs to a given group."""
        return self.groups.filter(name=group_name).exists()

    def soft_delete(self):
        """Soft-delete the user (prevents login)."""
        self.is_active = False
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(
            update_fields=["is_active", "is_deleted", "deleted_at", "updated_at"]
        )

    def hard_delete(self):
        """Permanently delete the user from the database."""
        super().delete()


class LoginHistory(models.Model):
    """Audit log for all login attempts (successful and failed)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,   # Keep history even if user is deleted
        null=True,
        blank=True,
        related_name="login_histories"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_name = models.CharField(max_length=100, blank=True)
    browser = models.CharField(max_length=50, blank=True)
    operating_system = models.CharField(max_length=50, blank=True)
    successful = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=255, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["successful"]),
        ]

    def __str__(self):
        email = self.user.email if self.user else "Unknown user"
        return f"{email} - {self.created_at}"


class UserSession(models.Model):
    """
    Session tracking using JWT ID (jti) for refresh tokens.
    Does NOT store the actual tokens – only metadata for revocation.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    jti = models.CharField(max_length=255, unique=True, db_index=True)
    device_name = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    browser = models.CharField(max_length=50, blank=True)
    operating_system = models.CharField(max_length=50, blank=True)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False, db_index=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["jti"]),
            models.Index(fields=["user", "revoked"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.device_name} ({self.created_at})"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def revoke(self):
        self.revoked = True
        self.revoked_at = timezone.now()
        self.save(update_fields=["revoked", "revoked_at", "last_activity"])


# ─── Profile Models for each User Type ──────────────────────────────

class AgentProfile(models.Model):
    """Profile for Call Center Agents."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='agent_profile'
    )
    extension = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    assigned_queue = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Agent Profile"
        verbose_name_plural = "Agent Profiles"

    def __str__(self):
        return f"Agent: {self.user.email}"


class SupervisorProfile(models.Model):
    """Profile for Supervisors."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='supervisor_profile'
    )
    team_size = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Supervisor Profile"
        verbose_name_plural = "Supervisor Profiles"

    def __str__(self):
        return f"Supervisor: {self.user.email}"


class DispatcherProfile(models.Model):
    """Profile for Dispatchers."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dispatcher_profile'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dispatcher Profile"
        verbose_name_plural = "Dispatcher Profiles"

    def __str__(self):
        return f"Dispatcher: {self.user.email}"


class ManagerProfile(models.Model):
    """Profile for Managers."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='manager_profile'
    )
    is_active = models.BooleanField(default=True)
    department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Manager Profile"
        verbose_name_plural = "Manager Profiles"

    def __str__(self):
        return f"Manager: {self.user.email}"


class CompanyProfile(models.Model):
    """Profile for Company/B2B client admins."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_profile'
    )
    company_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company Profile"
        verbose_name_plural = "Company Profiles"

    def __str__(self):
        return f"Company: {self.user.email}"


class AdminProfile(models.Model):
    """Profile for System Admins."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_profile'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admin Profile"
        verbose_name_plural = "Admin Profiles"

    def __str__(self):
        return f"Admin: {self.user.email}"