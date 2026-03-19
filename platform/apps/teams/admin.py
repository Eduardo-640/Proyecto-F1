from django.contrib import admin
from apps.races.models import CreditTransaction
from .models import Team, Sponsor, SponsorCondition


class SponsorConditionInline(admin.TabularInline):
    model = SponsorCondition
    extra = 1
    fields = ["type", "category", "value", "description"]
    readonly_fields = []


class SponsorInline(admin.TabularInline):
    model = Sponsor
    extra = 1
    fields = ["name", "is_main", "base_bonus", "active"]
    readonly_fields = []


class CreditTransactionInline(admin.TabularInline):
    model = CreditTransaction
    extra = 0
    fields = ["amount", "transaction_type", "description", "race", "created_at"]
    readonly_fields = [
        "amount",
        "transaction_type",
        "description",
        "race",
        "created_at",
    ]


# re-register TeamAdmin with credit transactions inline
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["name", "credits", "active", "created_at"]
    list_filter = ["active"]
    search_fields = ["name"]
    inlines = [SponsorInline, CreditTransactionInline]


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ["name", "team", "is_main", "base_bonus", "active"]
    list_filter = ["is_main", "active"]
    search_fields = ["name", "team__name"]
    inlines = [SponsorConditionInline]


@admin.register(SponsorCondition)
class SponsorConditionAdmin(admin.ModelAdmin):
    list_display = ["sponsor", "type", "category", "value", "description"]
    list_filter = ["type", "category"]
    search_fields = ["sponsor__name", "description"]
