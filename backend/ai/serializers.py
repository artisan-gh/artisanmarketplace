from rest_framework import serializers
from .models import AIModel, AIRequest


class AIModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = (
            'id', 'name', 'version', 'description', 'provider', 'model_type',
            'model_id', 'config', 'max_tokens', 'cost_per_1k_tokens',
            'is_active', 'is_default', 'total_requests', 'total_successful',
            'total_failed', 'created_at', 'updated_at'
        )
        read_only_fields = ('total_requests', 'total_successful', 'total_failed', 'created_at', 'updated_at')


class AIModelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = ('id', 'name', 'version', 'provider', 'model_type', 'is_active', 'is_default')


class AIRequestSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    duration_seconds = serializers.FloatField(read_only=True)

    class Meta:
        model = AIRequest
        fields = (
            'id', 'request_id', 'user', 'user_email', 'model', 'model_name',
            'request_type', 'input_data', 'output_data', 'metadata',
            'tokens_used', 'tokens_prompt', 'tokens_completion',
            'latency_ms', 'cost', 'status', 'error_message', 'error_code',
            'started_at', 'completed_at', 'duration_seconds', 'ip_address',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'request_id', 'status', 'error_message', 'error_code',
            'started_at', 'completed_at', 'created_at', 'updated_at'
        )


class AIRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIRequest
        fields = ('model', 'request_type', 'input_data', 'metadata')


class AIRequestStatsSerializer(serializers.Serializer):
    total_requests = serializers.IntegerField()
    successful = serializers.IntegerField()
    failed = serializers.IntegerField()
    pending = serializers.IntegerField()
    avg_latency = serializers.FloatField()
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=6)
    total_tokens = serializers.IntegerField()