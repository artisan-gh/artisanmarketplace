import django_filters
from .models import AuditLog
from .choices import AuditAction, AuditSeverity, HttpMethod


class AuditLogFilter(django_filters.FilterSet):
    user = django_filters.UUIDFilter(field_name="user__id")
    action = django_filters.ChoiceFilter(choices=AuditAction.choices)
    severity = django_filters.ChoiceFilter(choices=AuditSeverity.choices)
    module = django_filters.CharFilter(lookup_expr="icontains")
    created_at__date = django_filters.DateFilter(field_name="created_at", lookup_expr="date")
    created_at_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    success = django_filters.BooleanFilter()
    archived = django_filters.BooleanFilter()

    class Meta:
        model = AuditLog
        fields = [
            "user",
            "action",
            "severity",
            "module",
            "created_at",
            "success",
            "archived",
            "response_status",
        ]