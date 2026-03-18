from django.contrib import admin
from .models import Driver, DriverStanding


class DriverStandingInline(admin.TabularInline):
    model = DriverStanding
    extra = 0
    fields = [
        "season",
        "total_points",
        "races_entered",
        "wins",
        "podiums",
        "pole_positions",
        "fastest_laps",
        "dnf_count",
    ]
    readonly_fields = []


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ["name", "team", "steam_id", "active", "created_at"]
    list_filter = ["active", "team"]
    search_fields = ["name", "steam_id", "team__name"]
    inlines = [DriverStandingInline]


@admin.register(DriverStanding)
class DriverStandingAdmin(admin.ModelAdmin):
    list_display = [
        "driver",
        "season",
        "total_points",
        "races_entered",
        "wins",
        "podiums",
        "pole_positions",
        "fastest_laps",
        "dnf_count",
    ]
    list_filter = ["season"]
    search_fields = ["driver__name", "season__name"]
