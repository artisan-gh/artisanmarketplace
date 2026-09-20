
from rest_framework import serializers

PHONE_RE = r"^\+?[0-9]{9,15}$"


class SendOTPSerializer(serializers.Serializer):
    phone = serializers.RegexField(PHONE_RE, error_messages={"invalid": "Enter a valid phone number."})
    def validate_phone(self, value):
        return value.replace(" ", "").replace("-", "")


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.RegexField(PHONE_RE)
    code = serializers.RegexField(r"^[0-9]{6}$")
    def validate_phone(self, value):
        return value.replace(" ", "").replace("-", "")
