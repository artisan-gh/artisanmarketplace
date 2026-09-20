
from django.urls import path
from .views_otp import ResendOTPView, SendOTPView, VerifyOTPView

app_name = "client_auth"

urlpatterns = [
    path("otp/send/", SendOTPView.as_view(), name="otp_send"),
    path("otp/resend/", ResendOTPView.as_view(), name="otp_resend"),
    path("otp/verify/", VerifyOTPView.as_view(), name="otp_verify"),
]
