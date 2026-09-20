
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views_client import (
    ClientInvoiceViewSet,
    PublicInvoicePayView,
    PublicInvoiceView,
)

app_name = "billing_client"

router = DefaultRouter()
router.register(r"", ClientInvoiceViewSet, basename="client-invoice")

urlpatterns = [
    path("public/<str:token>/pay/", PublicInvoicePayView.as_view(), name="public-invoice-pay"),
    path("public/<str:token>/", PublicInvoiceView.as_view(), name="public-invoice"),
    *router.urls,
]
