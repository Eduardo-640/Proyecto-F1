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

        UPFRONT_PERCENT = 0.25
        UPFRONT_CAP = 2000

        applied = []
        skipped = []
        with transaction.atomic():
            for team in queryset:
                dev, _ = TeamDevelopment.objects.get_or_create(team=team, season=season)
                bonuses = service_apply_starting_bonuses(dev)

                # ── Department bonuses audit log ──────────────────────────
                if bonuses:
                    CreditTransaction.objects.create(
                        team=team,
                        amount=0,
                        transaction_type=RaceTransactionType.ADMIN_ADJUSTMENT,
                        description=(
                            f"Starting bonuses applied: {', '.join(sorted(bonuses))} "
                            f"(sponsor={getattr(team.sponsors.filter(is_main=True).first(), 'name', 'None')}, season={season})"
                        ),
                    )

                # ── Sponsor upfront + SponsorPayout (always, independent of dept bonuses) ──
                try:
                    sponsor = team.sponsors.filter(is_main=True, active=True).first()
                except Exception:
                    sponsor = None

                if sponsor and (sponsor.base_bonus or 0) > 0:
                    amount = sponsor.base_bonus
                    upfront = min(int(round(amount * UPFRONT_PERCENT)), UPFRONT_CAP)
                    remainder = amount - upfront

                    marker = f"sponsor_base:season:{season.id}:sponsor:{sponsor.id}"
                    already_paid = CreditTransaction.objects.filter(
                        team=team,
                        transaction_type=RaceTransactionType.SPONSOR_BASE,
                        description__contains=marker,
                    ).exists()

                    if not already_paid and upfront > 0:
                        team.credits = (team.credits or 0) + upfront
                        team.save(update_fields=["credits"])
                        CreditTransaction.objects.create(
                            team=team,
                            amount=upfront,
                            transaction_type=RaceTransactionType.SPONSOR_BASE,
                            description=f"Sponsor upfront {sponsor.name} ({marker})",
                        )

                    if remainder > 0:
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

                if bonuses:
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
            path(
                "balance/",
                self.admin_site.admin_view(self.balance_sponsors),
                name="teams_sponsor_balance",
            ),
            path(
                "export-csv/",
                self.admin_site.admin_view(self.export_csv),
                name="teams_sponsor_export_csv",
            ),
        ]
        return custom + urls

    def export_csv(self, request):
        """Export all sponsors to a semicolon-delimited CSV in the same format as import."""
        CATS = [
            "engine",
            "aerodynamics",
            "electronics",
            "chassis",
            "suspension",
            "development",
            "consistency",
            "podiums",
            "wins",
            "points",
            "speed",
            "money",
        ]
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="sponsors_export.csv"'
        response.write("\ufeff")  # UTF-8 BOM so Excel opens it correctly
        writer = csv.writer(response, delimiter=";")
        writer.writerow(
            ["name", "description", "base_bonus", "is_main", "active"] + CATS
        )
        for sponsor in Sponsor.objects.prefetch_related("conditions").order_by("id"):
            cond_map = {c.category: c.value for c in sponsor.conditions.all()}
            row = [
                sponsor.name,
                sponsor.description,
                sponsor.base_bonus,
                "true" if sponsor.is_main else "false",
                "true" if sponsor.active else "false",
            ] + [cond_map.get(cat, 0) for cat in CATS]
            writer.writerow(row)
        return response

    def balance_sponsors(self, request):
        """Fill missing SponsorCondition rows and rebalance affinities/penalties (total_score == 0)."""
        import random
        from .constants import Affinity

        NON_MONEY_CATS = [c for c in [v for v, _ in Affinity.choices] if c != "money"]
        ALL_CATS = NON_MONEY_CATS + ["money"]

        filled = 0
        rebalanced = 0

        for sponsor in Sponsor.objects.prefetch_related("conditions").all():
            existing = {c.category: c for c in sponsor.conditions.all()}

            # Fill missing categories
            for cat in ALL_CATS:
                if cat not in existing:
                    val = 1 if cat == "money" else 0
                    typ = "money" if cat == "money" else "neutral"
                    cond = SponsorCondition.objects.create(
                        sponsor=sponsor,
                        type=typ,
                        category=cat,
                        value=val,
                        description=f"Auto-filled: {cat} {val}",
                    )
                    existing[cat] = cond
                    filled += 1

            # Rebalance
            non_money = [existing[c] for c in NON_MONEY_CATS if c in existing]
            total_score = sum(int(c.value) for c in non_money)
            iterations = 0
            while total_score != 0 and iterations < 20:
                iterations += 1
                if total_score < 0:
                    targets = [c for c in non_money if int(c.value) < 0]
                    if not targets:
                        break
                    victim = random.choice(targets)
                    victim.value = 0
                    victim.type = "neutral"
                    victim.description = f"Rebalanced: {victim.category}"
                    victim.save(update_fields=["value", "type", "description"])
                    total_score += 1
                else:
                    targets = [c for c in non_money if int(c.value) > 0]
                    if not targets:
                        break
                    victim = random.choice(targets)
                    victim.value = 0
                    victim.type = "neutral"
                    victim.description = f"Rebalanced: {victim.category}"
                    victim.save(update_fields=["value", "type", "description"])
                    total_score -= 1
                non_money = list(sponsor.conditions.exclude(category="money"))
                rebalanced += 1

            new_total = sum(
                int(c.value) for c in sponsor.conditions.exclude(category="money")
            )
            if sponsor.total_score != new_total:
                sponsor.total_score = new_total
                sponsor.save(update_fields=["total_score"])

        self.message_user(
            request,
            f"Balance complete: {filled} conditions filled, {rebalanced} adjustments made.",
            level=messages.SUCCESS,
        )
        return redirect("..")

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
            rows = list(reader)  # read all rows before deleting anything
            created = 0
            errors = []

            with transaction.atomic():
                # delete inside the transaction so a failed import rolls back
                SponsorCondition.objects.all().delete()
                Sponsor.objects.all().delete()
                for i, row in enumerate(rows, start=1):
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
                            "wins",
                            "points",
                            "speed",
                            "money",
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
                                typ = None
                            else:
                                val = 0 if v == 0 else (1 if v > 0 else -1)
                                typ = (
                                    "neutral"
                                    if val == 0
                                    else ("affinity" if val > 0 else "penalty")
                                )

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
