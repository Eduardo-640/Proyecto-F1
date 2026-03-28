from django.contrib import admin
from django.utils.html import format_html
from apps.races.models import RaceResult
from .models import Driver, DriverStanding, DriverPointTransaction, Usuario


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


class DriverPointTransactionInline(admin.TabularInline):
    model = DriverPointTransaction
    extra = 0
    fields = ["season", "amount", "description", "race", "created_at"]
    readonly_fields = ["season", "amount", "description", "race", "created_at"]


DriverAdmin.inlines = [DriverStandingInline, DriverPointTransactionInline]


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['email', 'role', 'driver', 'active', 'created_at']
    list_filter = ['role', 'active']
    search_fields = ['email', 'driver__name', 'driver__last_name']
    autocomplete_fields = ['driver']
    readonly_fields = ['created_at']


@admin.register(DriverStanding)
class DriverStandingAdmin(admin.ModelAdmin):
    list_display = [
        "driver",
        "season",
        "total_points",
        "points_breakdown",
        "races_entered",
        "wins",
        "podiums",
        "pole_positions",
        "fastest_laps",
        "dnf_count",
    ]
    list_filter = ["season"]
    search_fields = ["driver__name", "season__name"]

    def points_breakdown(self, obj):
        # Show per-race contribution for this standing's season
        qs = (
            RaceResult.objects.filter(driver=obj.driver, race__season=obj.season)
            .select_related("race", "race__circuit")
            .order_by("race__round_number", "race__status")
        )
        if not qs.exists():
            return "-"
        parts = []
        for rr in qs:
            pts = rr.points_awarded or 0
            status = rr.race.status or ""
            parts.append(
                f"R{rr.race.round_number} {rr.race.circuit.name} ({status}): {pts}"
            )
        return format_html("<br/>".join(parts))

    points_breakdown.short_description = "Points breakdown"
