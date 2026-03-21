from django.contrib import admin
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import path
from django.template.response import TemplateResponse
from django.template import TemplateDoesNotExist
from django.http import HttpResponse
from django.contrib import messages
import csv
import io

from apps.races.models import CreditTransaction
from apps.races.constants import TransactionType as RaceTransactionType
from apps.seasons.models import Season
from apps.developments.models import TeamDevelopment
from apps.developments.setup_service import (
    apply_starting_bonuses as service_apply_starting_bonuses,
)
from .models import Team, Sponsor, SponsorCondition, SponsorPayout


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
    actions = [
        "assign_main_sponsors",
        "unassign_main_sponsors",
        "apply_starting_bonuses",
    ]

    def assign_main_sponsors(self, request, queryset):
        """Assign available sponsor templates (team=NULL) as main sponsors to selected teams.

        This action is idempotent: existing main sponsor for a team will be unset.
        If there are fewer sponsor templates than teams, templates are cycled.
        """
        if "apply" in request.POST:
            sponsor_qs = list(Sponsor.objects.filter(team__isnull=True, active=True))
            if not sponsor_qs:
                self.message_user(
                    request,
                    "No available sponsor templates (team is null).",
                    level=messages.ERROR,
                )
                return

            assigned = []
            with transaction.atomic():
                for i, team in enumerate(queryset):
                    # unset previous main sponsor(s)
                    Sponsor.objects.filter(team=team, is_main=True).update(
                        is_main=False, team=None
                    )

                    # pick a template (cycle if needed)
                    template = sponsor_qs[i % len(sponsor_qs)]
                    # assign template to team as main sponsor
                    template.team = team
                    template.is_main = True
                    template.save(update_fields=["team", "is_main"])
                    assigned.append(str(team))

            self.message_user(
                request,
                f"Assigned sponsors to {len(assigned)} team(s): {', '.join(assigned)}",
                level=messages.SUCCESS,
            )
            return None

        # initial confirmation page (attempt to render template, fallback to inline HTML)
        context = dict(
            self.admin_site.each_context(request),
            teams=queryset,
            opts=self.model._meta,
        )
        try:
            return TemplateResponse(
                request, "admin/teams/assign_sponsors_confirm.html", context
            )
        except TemplateDoesNotExist:
            # Fallback to the built-in admin action confirmation template
            try:
                return render(request, "admin/action_confirmation.html", context)
            except TemplateDoesNotExist:
                # Last-resort simple message
                return HttpResponse(
                    "<html><body><h1>Confirm sponsor assignment</h1><p>Template not available.</p></body></html>"
                )

    assign_main_sponsors.short_description = (
        "Assign available main sponsors to selected teams"
    )

    def unassign_main_sponsors(self, request, queryset):
        """Remove main sponsor assignment from selected teams (team field nulled, is_main=False)."""
        with transaction.atomic():
            count = 0
            for team in queryset:
                updated = Sponsor.objects.filter(team=team, is_main=True).update(
                    is_main=False, team=None
                )
                count += updated
        self.message_user(
            request,
            f"Unassigned main sponsors from {count} sponsor record(s).",
            level=messages.SUCCESS,
        )

    unassign_main_sponsors.short_description = (
        "Unassign main sponsors from selected teams"
    )

    def apply_starting_bonuses(self, request, queryset):
        """Apply sponsor-derived starting bonuses for selected teams.

        Uses the active Season if present, otherwise the most recent by start_date.
        Creates `TeamDevelopment` rows if missing.
        """
        # Determine target season
        season = Season.objects.filter(active=True).first()
        if season is None:
            season = Season.objects.order_by("-start_date").first()

        if season is None:
            self.message_user(
                request,
                "No season available. Create a Season first.",
                level=messages.ERROR,
            )
            return

        applied = []
        skipped = []
        with transaction.atomic():
            for team in queryset:
                dev, _ = TeamDevelopment.objects.get_or_create(team=team, season=season)
                bonuses = service_apply_starting_bonuses(dev)
                if bonuses:
                    # Create an audit transaction (amount 0) to record the bonus application
                    CreditTransaction.objects.create(
                        team=team,
                        amount=0,
                        transaction_type=RaceTransactionType.ADMIN_ADJUSTMENT,
                        description=(
                            f"Starting bonuses applied: {', '.join(sorted(bonuses))} "
                            f"(sponsor={getattr(team.sponsors.filter(is_main=True).first(), 'name', 'None')}, season={season})"
                        ),
                    )
                    # Also apply sponsor monetary upfront (same policy as apply_sponsor_base)
                    try:
                        sponsor = team.sponsors.filter(
                            is_main=True, active=True
                        ).first()
                    except Exception:
                        sponsor = None

                    if sponsor and (sponsor.base_bonus or 0) > 0:
                        amount = sponsor.base_bonus or 0
                        UPFRONT_PERCENT = 0.25
                        UPFRONT_CAP = 2000
                        upfront = int(round(amount * UPFRONT_PERCENT))
                        upfront = min(upfront, UPFRONT_CAP)
                        remainder = amount - upfront

                        # idempotency marker (same format as management command)
                        marker = f"sponsor_base:season:{season.id}:sponsor:{sponsor.id}"
                        exists = CreditTransaction.objects.filter(
                            team=team,
                            transaction_type=RaceTransactionType.SPONSOR_BASE,
                            description__contains=marker,
                        ).exists()

                        if not exists and upfront > 0:
                            team.credits = (team.credits or 0) + upfront
                            team.save(update_fields=["credits"])
                            CreditTransaction.objects.create(
                                team=team,
                                amount=upfront,
                                transaction_type=RaceTransactionType.SPONSOR_BASE,
                                description=f"Sponsor upfront {sponsor.name} ({marker})",
                            )

                        if remainder > 0:
                            # avoid duplicating SponsorPayouts for same season/sponsor/team
                            dup = SponsorPayout.objects.filter(
                                sponsor=sponsor, team=team, season=season
                            ).exists()
                            if not dup:
                                SponsorPayout.objects.create(
                                    sponsor=sponsor,
                                    team=team,
                                    season=season,
                                    total_amount=amount,
                                    remaining_amount=remainder,
                                )
                    applied.append(f"{team}: {', '.join(sorted(bonuses))}")
                else:
                    skipped.append(str(team))

        msg = []
        if applied:
            msg.append(
                f"Applied bonuses to {len(applied)} team(s): {', '.join(applied)}"
            )
        if skipped:
            msg.append(
                f"Skipped {len(skipped)} team(s) with no applicable sponsor or already applied."
            )

        level = messages.SUCCESS if applied else messages.INFO
        self.message_user(request, "; ".join(msg), level=level)

    apply_starting_bonuses.short_description = (
        "Apply sponsor starting bonuses to selected teams (active season)"
    )


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ["name", "team", "is_main", "base_bonus", "active"]
    list_filter = ["is_main", "active"]
    search_fields = ["name", "team__name"]
    inlines = [SponsorConditionInline]
    change_list_template = "admin/teams/sponsor_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "import-csv/",
                self.admin_site.admin_view(self.import_csv),
                name="teams_sponsor_import_csv",
            ),
        ]
        return custom + urls

    def import_csv(self, request):
        """Simple CSV import endpoint for sponsors. Expects semicolon-delimited CSV with headers:
        name;description;base_bonus;is_main;active;engine;aerodynamics;electronics;chassis;suspension;development;consistency;podiums;money;speed
        This view will delete all existing sponsors and recreate them from the CSV.
        """
        if request.method == "POST":
            f = request.FILES.get("csv_file")
            if not f:
                self.message_user(request, "No file uploaded", level=messages.ERROR)
                return redirect("..")

            text = f.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text), delimiter=";")
            created = 0
            errors = []
            # delete existing sponsors and conditions
            SponsorCondition.objects.all().delete()
            Sponsor.objects.all().delete()

            with transaction.atomic():
                for i, row in enumerate(reader, start=1):
                    try:
                        name = row.get("name", f"Sponsor {i}").strip()
                        sponsor = Sponsor.objects.create(
                            name=name,
                            description=row.get("description", "").strip(),
                            is_main=row.get("is_main", "false").lower()
                            in ("1", "true", "yes"),
                            base_bonus=max(0, int(row.get("base_bonus") or 0)),
                            active=row.get("active", "true").lower()
                            in ("1", "true", "yes"),
                        )

                        # build conditions for all expected categories
                        cats = [
                            "engine",
                            "aerodynamics",
                            "electronics",
                            "chassis",
                            "suspension",
                            "development",
                            "consistency",
                            "podiums",
                            "money",
                            "speed",
                        ]
                        total = 0
                        for cat in cats:
                            raw = row.get(cat, "0")
                            try:
                                v = int(raw)
                            except Exception:
                                v = 0
                            if cat == "money":
                                val = max(1, v) if v != 0 else 1
                                typ = "money"
                            else:
                                val = 0 if v == 0 else (1 if v > 0 else -1)
                                typ = (
                                    "neutral"
                                    if val == 0
                                    else ("affinity" if val > 0 else "penalty")
                                )

                            # Only create non-money conditions if value != 0 (skip neutral to avoid clutter).
                            if cat == "money" or val != 0:
                                SponsorCondition.objects.create(
                                    sponsor=sponsor,
                                    type=typ,
                                    category=cat,
                                    value=val,
                                    description=f"Imported: {cat} {val}",
                                )

                            if cat != "money":
                                total += int(val)

                        sponsor.total_score = int(total)
                        sponsor.save(update_fields=["total_score"])
                        created += 1
                    except Exception as e:
                        errors.append(f"Row {i}: {e}")

            if errors:
                for e in errors:
                    self.message_user(request, e, level=messages.ERROR)
            self.message_user(
                request, f"Imported {created} sponsors", level=messages.SUCCESS
            )
            return redirect("..")

        # render upload form using proper template so csrf token is included
        return render(request, "admin/teams/import_sponsors_form.html", {})


@admin.register(SponsorCondition)
class SponsorConditionAdmin(admin.ModelAdmin):
    list_display = ["sponsor", "type", "category", "value", "description"]
    list_filter = ["type", "category"]
    search_fields = ["sponsor__name", "description"]
