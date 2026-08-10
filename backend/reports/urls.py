from django.urls import path
from .views import (
    IncidentReportView,
    ArtisanPerformanceReportView,
    CallCenterReportView,
    CustomerReportView,
    ExportReportView,
)

app_name = 'reports'

urlpatterns = [
    path('incidents/', IncidentReportView.as_view(), name='incident-report'),
    path('artisans/', ArtisanPerformanceReportView.as_view(), name='artisan-performance'),
    path('calls/', CallCenterReportView.as_view(), name='call-center-report'),
    path('customers/', CustomerReportView.as_view(), name='customer-report'),
    path('export/', ExportReportView.as_view(), name='export-report'),
]