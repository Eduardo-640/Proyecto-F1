from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    driver_name = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'email', 'role', 'active', 'created_at', 'driver', 'driver_name']
        read_only_fields = ['id', 'created_at']

    def get_driver_name(self, obj):
        if obj.driver:
            return f"{obj.driver.name} {obj.driver.last_name or ''}".strip()
        return None


class UsuarioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['email', 'role', 'driver', 'active']
