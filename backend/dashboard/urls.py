from django.urls import path
from .views import (
    DashboardSummaryView,
    AgentDashboardView,
    ArtisanDashboardView,
    SupervisorDashboardView,
)

app_name = 'dashboard'

urlpatterns = [
    path('summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('agent/', AgentDashboardView.as_view(), name='agent-dashboard'),
    path('artisan/', ArtisanDashboardView.as_view(), name='artisan-dashboard'),
    path('supervisor/', SupervisorDashboardView.as_view(), name='supervisor-dashboard'),
]