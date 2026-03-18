from django.contrib import admin
from .models import Season


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "year",
        "edition",
        "active",
        "created_at",
        "start_date",
        "end_date",
    ]
    list_filter = ["active", "year"]
