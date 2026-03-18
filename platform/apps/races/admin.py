from django.contrib import admin
from .models import Race, RaceResult, CreditTransaction, Circuit


class RaceResultInline(admin.TabularInline):
    model = RaceResult
    extra = 1
    fields = [
        "driver",
        "team",
        "position",
        "pole_position",
        "fastest_lap",
        "finished_race",
        "points_awarded",
    ]
    readonly_fields = []


class CreditTransactionInline(admin.TabularInline):
    model = CreditTransaction
    extra = 1
    fields = ["team", "amount", "transaction_type", "description"]
    readonly_fields = []


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ["season", "round_number", "circuit", "race_date", "status"]
    list_filter = ["season", "status"]
    search_fields = ["circuit__name", "season__name"]
    inlines = [RaceResultInline, CreditTransactionInline]


@admin.register(Circuit)
class CircuitAdmin(admin.ModelAdmin):
    list_display = ["name", "location", "laps", "length_km"]
    search_fields = ["name", "location"]
