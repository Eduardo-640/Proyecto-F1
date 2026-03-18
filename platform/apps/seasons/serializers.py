from rest_framework import serializers
from .models import Season


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = [
            "id",
            "name",
            "year",
            "edition",
            "active",
            "created_at",
            "start_date",
            "end_date",
        ]
        read_only_fields = ["created_at"]
