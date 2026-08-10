from rest_framework import serializers
from .models import AppSetting


class AppSettingSerializer(serializers.ModelSerializer):
    parsed_value = serializers.SerializerMethodField()
    data_type_display = serializers.CharField(source='get_data_type_display', read_only=True)
    group_display = serializers.CharField(source='get_group_display', read_only=True)

    class Meta:
        model = AppSetting
        fields = (
            'id', 'key', 'value', 'parsed_value', 'data_type', 'data_type_display',
            'group', 'group_display', 'description', 'is_public', 'is_editable',
            'is_required', 'options', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')


class AppSettingPublicSerializer(serializers.ModelSerializer):
    parsed_value = serializers.SerializerMethodField()

    class Meta:
        model = AppSetting
        fields = ('key', 'parsed_value')

    def get_parsed_value(self, obj):
        return obj.parsed_value


class AppSettingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSetting
        fields = ('value',)