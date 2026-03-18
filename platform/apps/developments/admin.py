from django.contrib import admin
from .models import TeamDevelopment, PurchasedUpgrade


@admin.register(TeamDevelopment)
class TeamDevelopmentAdmin(admin.ModelAdmin):
    list_display = [
        "team",
        "season",
        "engine",
        "aerodynamics",
        "chassis",
        "suspension",
        "electronics",
        "updated_at",
    ]
    list_filter = ["season"]
    search_fields = ["team__name", "season__name"]


@admin.register(PurchasedUpgrade)
class PurchasedUpgradeAdmin(admin.ModelAdmin):
    list_display = [
        "team",
        "season",
        "department",
        "previous_level",
        "new_level",
        "cost",
        "applied",
        "purchased_at",
    ]
    list_filter = ["season", "department", "applied"]
    search_fields = ["team__name", "season__name", "department"]
