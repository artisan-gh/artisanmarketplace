"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

# drf-yasg
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from incident_category.views import (
    PublicIncidentCategoryListView,
    PublicSubCategoryListView,
)
# =============================================================================
# API Schema (Swagger / Redoc)
# =============================================================================

schema_view = get_schema_view(
    openapi.Info(
        title="Artisan Marketplace API",
        default_version='v1',
        description="API for connecting artisans with clients.",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# =============================================================================
# URL Patterns
# =============================================================================

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # API Authentication (accounts app)
    path("api/auth/", include("accounts.urls")),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("api/categories/", include("categories.urls")),
    
    path('api/services/', include('services.urls')),
    path('api/artisans/', include('artisans.urls')),
    path('api/clients/', include('clients.urls')),
    path('api/companies/', include('companies.urls')),
    
    
    
    path('api/payments/', include('payments.urls')),
    path('api/wallets/', include('wallets.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/invoices/', include('invoices.urls')),
    
    
    path("api/notifications/", include("notifications.urls")),
    path('api/support/', include('support.urls')),
    
    
    path('api/ai/', include('ai.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/sla/', include('sla.urls')),
    path('api/billing/', include('billing.urls')),
    
    
    path('api/verification/', include('verification.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/app-settings/', include('app_settings.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/media/', include('media.urls')),
    
    path('api/organizations/', include('organizations.urls')),
    
    path('api/learning/', include('learning.urls')),
    path('api/recruitment/', include('recruitment.urls')),
    path('api/call-center/', include('call_center.urls')),
    path("api/customers/", include("customers.urls")),
    path('api/incident-categories/', include('incident_category.urls')),
    path('api/incident-priorities/', include('incident_priority.urls')),
    path('api/incident-statuses/', include('incident_statuses.urls')),
    path('api/incidents/', include('incidents.urls')),
    path('api/attachments/', include('attachments.urls')),
    path('api/comments/', include('comments.urls')),
    path('api/assignments/', include('assignments.urls')),

    # Swagger / Redoc (drf-yasg)
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("swagger.json/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    
    path('api/public/categories/', PublicIncidentCategoryListView.as_view(), name='public-categories'),
    path('api/public/subcategories/', PublicSubCategoryListView.as_view(), name='public-subcategories'),
]

# =============================================================================
# Serve static and media files in development
# =============================================================================

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
