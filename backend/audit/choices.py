from django.db import models


class AuditAction(models.TextChoices):
    CREATE = "CREATE", "Create"
    UPDATE = "UPDATE", "Update"
    DELETE = "DELETE", "Delete"
    SOFT_DELETE = "SOFT_DELETE", "Soft Delete"
    RESTORE = "RESTORE", "Restore"
    LOGIN = "LOGIN", "Login"
    LOGOUT = "LOGOUT", "Logout"
    VIEW = "VIEW", "View"
    EXPORT = "EXPORT", "Export"
    IMPORT = "IMPORT", "Import"
    DOWNLOAD = "DOWNLOAD", "Download"
    UPLOAD = "UPLOAD", "Upload"
    PRINT = "PRINT", "Print"
    LOCK = "LOCK", "Lock"
    UNLOCK = "UNLOCK", "Unlock"
    ARCHIVE = "ARCHIVE", "Archive"
    UNARCHIVE = "UNARCHIVE", "Unarchive"
    MERGE = "MERGE", "Merge"
    SPLIT = "SPLIT", "Split"
    VERIFY = "VERIFY", "Verify"
    UNVERIFY = "UNVERIFY", "Unverify"
    ASSIGN = "ASSIGN", "Assign"
    REASSIGN = "REASSIGN", "Reassign"
    ESCALATE = "ESCALATE", "Escalate"
    APPROVE = "APPROVE", "Approve"
    REJECT = "REJECT", "Reject"
    COMPLETE = "COMPLETE", "Complete"


class AuditSeverity(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"
    CRITICAL = "CRITICAL", "Critical"


class HttpMethod(models.TextChoices):
    GET = "GET", "GET"
    POST = "POST", "POST"
    PUT = "PUT", "PUT"
    PATCH = "PATCH", "PATCH"
    DELETE = "DELETE", "DELETE"
    OPTIONS = "OPTIONS", "OPTIONS"
    HEAD = "HEAD", "HEAD"