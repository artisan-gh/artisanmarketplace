
from django.urls import path

from .views import (
    AssessmentDetailView,
    AssessmentListView,
    ResetAttemptsView,
    ResultView,
    StartAttemptView,
    SubmitAttemptView,
)

app_name = "provider"

urlpatterns = [
    path("assessments/", AssessmentListView.as_view(), name="assessment-list"),
    path("assessments/<slug:slug>/", AssessmentDetailView.as_view(), name="assessment-detail"),
    path("assessments/<slug:slug>/start/", StartAttemptView.as_view(), name="assessment-start"),
    path("attempts/<int:pk>/submit/", SubmitAttemptView.as_view(), name="attempt-submit"),
    path("attempts/<int:pk>/result/", ResultView.as_view(), name="attempt-result"),
    path("assessments/<slug:slug>/reset/", ResetAttemptsView.as_view(), name="assessment-reset"),
]
