"""
Django admin configuration for the developments app.

Bulk operations are managed through **AccionMasiva** — a single entry point
that targets one season (and, optionally, one team) and logs results.
Individual model admins retain lightweight save_model overrides for the
operations that are naturally triggered by a single-object save.
"""

from __future__ import annotations

import traceback

from django.contrib import admin, messages
from django.db import transaction
from django.utils import timezone

from .models import (
    AccionMasiva,
    BalanceOfPerformance,
    CarSetupSnapshot,
    CircuitEmphasis,
    CircuitSetup,
    PurchasedUpgrade,
    TeamDevelopment,
)
from .setup_service import (
    apply_starting_bonuses,
    apply_upgrade_to_setup,
    generate_circuit_setup,
    generate_initial_preset,
)


# ---------------------------------------------------------------------------
# AccionMasiva — centralized bulk-action executor
# ---------------------------------------------------------------------------


def _execute_accion(accion: AccionMasiva) -> tuple[bool, list[str]]:
    """Execute the bulk action described by *accion* and return ``(ok, log_lines)``.

    Pure function — does NOT save the model; the caller (save_model or the
    re-run admin action) is responsible for persisting status/result_log.
    """
    lines: list[str] = []
    ok = True

    try:
        devs_qs = TeamDevelopment.objects.filter(season=accion.season).select_related(
            "team", "season"
        )
        if accion.team:
            devs_qs = devs_qs.filter(team=accion.team)
        devs = list(devs_qs)

        if not devs:
            return False, [
                "No TeamDevelopment records found for the selected season/team. "
                "Create TeamDevelopment rows first."
            ]

        # ------------------------------------------------------------------ #
        # INIT_PRESETS — generate version-1 snapshot for each team           #
        # ------------------------------------------------------------------ #
        if accion.action_type == AccionMasiva.ActionType.INIT_PRESETS:
            for dev in devs:
                try:
                    with transaction.atomic():
                        snap = generate_initial_preset(dev, bias=accion.bias or None)
                    lines.append(
                        f"OK   {dev.team}: preset '{snap.preset_bias}' created (v{snap.version})."
                    )
                except ValueError as exc:
                    lines.append(f"SKIP {dev.team}: {exc}")
                except Exception as exc:
                    lines.append(f"ERR  {dev.team}: {exc}")
                    ok = False

        # ------------------------------------------------------------------ #
        # APPLY_BONUSES — +1 level from main sponsor affinity                #
        # ------------------------------------------------------------------ #
        elif accion.action_type == AccionMasiva.ActionType.APPLY_BONUSES:
            for dev in devs:
                try:
                    bonuses = apply_starting_bonuses(dev)
                    if bonuses:
                        lines.append(
                            f"OK   {dev.team}: +1 on {', '.join(sorted(bonuses))}."
                        )
                    else:
                        lines.append(f"SKIP {dev.team}: no sponsor bonus applicable.")
                except Exception as exc:
                    lines.append(f"ERR  {dev.team}: {exc}")
                    ok = False

        # ------------------------------------------------------------------ #
        # GENERATE_CIRCUIT_SETUPS — race-weekend setups for one circuit      #
        # ------------------------------------------------------------------ #
        elif accion.action_type == AccionMasiva.ActionType.GENERATE_CIRCUIT_SETUPS:
            if not accion.circuit:
                return False, [
                    "A circuit must be selected for 'Generate Circuit Setups'. "
                    "Set the Circuit field and re-run."
                ]
            for dev in devs:
                try:
                    cs = generate_circuit_setup(dev, accion.circuit)
                    bop_note = " (BOP applied)" if "BALLAST" in cs.ini_content else ""
                    lines.append(
                        f"OK   {dev.team} @ {accion.circuit}: INI generated{bop_note}."
                    )
                except Exception as exc:
                    lines.append(f"ERR  {dev.team}: {exc}")
                    ok = False

        else:
            return False, [f"Unknown action type: {accion.action_type!r}"]

    except Exception as exc:
        lines.append(f"FATAL ERROR during setup: {exc}")
        lines.append(traceback.format_exc())
        ok = False

    return ok, lines


@admin.register(AccionMasiva)
class AccionMasivaAdmin(admin.ModelAdmin):
    list_display = [
        "action_type",
        "season",
        "team_label",
        "circuit",
        "status",
        "created_at",
        "executed_at",
    ]
    list_filter = ["season", "action_type", "status"]
    search_fields = ["season__name", "team__name"]
    readonly_fields = ["status", "result_log", "created_at", "executed_at"]
    actions = ["rerun_action"]

    fieldsets = [
        (
            "Acción",
            {
                "fields": ["action_type", "season", "team"],
                "description": (
                    "Selecciona la acción y la temporada. "
                    "Deja 'team' en blanco para aplicar a TODOS los equipos. "
                    "Al guardar se ejecuta inmediatamente."
                ),
            },
        ),
        (
            "Opciones",
            {
                "fields": ["bias", "circuit"],
                "description": (
                    "'bias' solo se usa para 'Generate Initial Setup Presets'. "
                    "'circuit' solo es necesario para 'Generate Circuit Setups'."
                ),
            },
        ),
        (
            "Resultado",
            {
                "fields": ["status", "result_log", "created_at", "executed_at"],
                "classes": ["collapse"],
            },
        ),
    ]

    @admin.display(description="Team")
    def team_label(self, obj: AccionMasiva) -> str:
        return str(obj.team) if obj.team else "— All teams"

    def save_model(self, request, obj, form, change):
        if change:
            # Editing an existing record only updates fields, never re-runs.
            super().save_model(request, obj, form, change)
            return

        ok, lines = _execute_accion(obj)
        obj.status = AccionMasiva.Status.OK if ok else AccionMasiva.Status.ERROR
        obj.result_log = "\n".join(lines)
        obj.executed_at = timezone.now()
        super().save_model(request, obj, form, change)

        level = messages.SUCCESS if ok else messages.ERROR
        self.message_user(
            request,
            f"Acción '{obj.get_action_type_display()}' completada "
            f"({'OK' if ok else 'con errores'}) — {len(lines)} equipo(s) procesado(s). "
            "Consulta el Resultado en el registro.",
            level,
        )

    @admin.action(description="Re-run selected actions")
    def rerun_action(self, request, queryset):
        ran = errors = 0
        for accion in queryset:
            ok, lines = _execute_accion(accion)
            accion.status = AccionMasiva.Status.OK if ok else AccionMasiva.Status.ERROR
            accion.result_log = "\n".join(lines)
            accion.executed_at = timezone.now()
            accion.save(update_fields=["status", "result_log", "executed_at"])
            if ok:
                ran += 1
            else:
                errors += 1

        if ran:
            self.message_user(
                request,
                f"{ran} acción(es) re-ejecutada(s) correctamente.",
                messages.SUCCESS,
            )
        if errors:
            self.message_user(
                request,
                f"{errors} acción(es) con errores. Revisa los logs.",
                messages.ERROR,
            )


from . import setup_generator as sg

# ---------------------------------------------------------------------------
# TeamDevelopment
# ---------------------------------------------------------------------------


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
        "bonuses_applied",
        "performance_score",
        "updated_at",
    ]
    list_filter = ["season", "bonuses_applied"]
    search_fields = ["team__name", "season__name"]
    readonly_fields = ["bonuses_applied"]

    @admin.display(description="Perf. Score")
    def performance_score(self, obj: TeamDevelopment) -> str:
        try:
            return f"{sg.get_performance_rating(obj):.1f}"
        except Exception:
            return "—"


# ---------------------------------------------------------------------------
# PurchasedUpgrade
# ---------------------------------------------------------------------------


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

    def save_model(self, request, obj, form, change):
        """Validate level jump and evolve car setup when ``applied`` flips to True."""
        if obj.new_level != obj.previous_level + 1:
            self.message_user(
                request,
                f"Invalid upgrade: levels must increase by exactly 1 "
                f"({obj.previous_level} → {obj.new_level} is not allowed).",
                messages.ERROR,
            )
            return

        was_applied_before = (
            PurchasedUpgrade.objects.filter(pk=obj.pk, applied=True).exists()
            if obj.pk
            else False
        )
        super().save_model(request, obj, form, change)

        if not (obj.applied and not was_applied_before):
            return

        try:
            dev = TeamDevelopment.objects.get(team=obj.team, season=obj.season)
        except TeamDevelopment.DoesNotExist:
            self.message_user(
                request,
                f"No TeamDevelopment found for {obj.team} in {obj.season}. "
                "Create it first, then mark the upgrade as applied.",
                messages.ERROR,
            )
            return

        try:
            with transaction.atomic():
                setattr(dev, obj.department, obj.new_level)
                dev.save(update_fields=[obj.department, "updated_at"])
                snapshot = apply_upgrade_to_setup(dev, obj)
        except Exception as exc:
            self.message_user(
                request,
                f"Upgrade saved but setup evolution failed: {exc}",
                messages.ERROR,
            )
            return

        if snapshot:
            changed_keys = list(snapshot.changed_params)
            self.message_user(
                request,
                f"Setup updated → v{snapshot.version} "
                f"({len(changed_keys)} param(s) changed: "
                f"{', '.join(changed_keys[:6])}"
                f"{'…' if len(changed_keys) > 6 else ''}).",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "Upgrade applied but no INI parameters changed "
                "(synergy thresholds not yet crossed).",
                messages.INFO,
            )


# ---------------------------------------------------------------------------
# CarSetupSnapshot
# ---------------------------------------------------------------------------


@admin.register(CarSetupSnapshot)
class CarSetupSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        "team",
        "season",
        "version",
        "preset_bias",
        "changed_params_summary",
        "upgrade",
        "created_at",
    ]
    list_filter = ["season", "preset_bias"]
    search_fields = ["team__name", "season__name"]
    readonly_fields = [
        "team",
        "season",
        "version",
        "ini_content",
        "params_json",
        "changed_params",
        "preset_bias",
        "upgrade",
        "created_at",
    ]

    def has_add_permission(self, request):
        """Snapshots are always generated by the system — forbid manual creation."""
        return False

    @admin.display(description="Changed params")
    def changed_params_summary(self, obj: CarSetupSnapshot) -> str:
        if not obj.changed_params:
            return "— (initial)"
        keys = list(obj.changed_params.keys())
        return f"{len(keys)}: {', '.join(keys[:4])}{'…' if len(keys) > 4 else ''}"


# ---------------------------------------------------------------------------
# CircuitSetup
# ---------------------------------------------------------------------------


@admin.register(CircuitSetup)
class CircuitSetupAdmin(admin.ModelAdmin):
    list_display = [
        "team",
        "season",
        "circuit",
        "base_snapshot",
        "overrides_summary",
        "updated_at",
    ]
    list_filter = ["season", "circuit"]
    search_fields = ["team__name", "season__name", "circuit__name"]
    readonly_fields = ["ini_content", "base_snapshot", "updated_at"]

    @admin.display(description="Overrides")
    def overrides_summary(self, obj: CircuitSetup) -> str:
        if not obj.tunable_overrides:
            return "— (auto)"
        keys = list(obj.tunable_overrides.keys())
        return f"{len(keys)}: {', '.join(keys[:4])}{'…' if len(keys) > 4 else ''}"

    def save_model(self, request, obj, form, change):
        """Regenerate the INI whenever the circuit setup is saved."""
        try:
            dev = TeamDevelopment.objects.get(team=obj.team, season=obj.season)
        except TeamDevelopment.DoesNotExist:
            self.message_user(
                request,
                "No TeamDevelopment found for this team+season. "
                "Create it before configuring a circuit setup.",
                messages.ERROR,
            )
            return

        try:
            updated = generate_circuit_setup(
                dev, obj.circuit, tunable_overrides=obj.tunable_overrides or None
            )
        except Exception as exc:
            self.message_user(
                request,
                f"INI generation failed: {exc}",
                messages.ERROR,
            )
            return

        obj.ini_content = updated.ini_content
        obj.base_snapshot = updated.base_snapshot
        super().save_model(request, obj, form, change)
        self.message_user(
            request,
            f"INI regenerated for {obj.team} at {obj.circuit}.",
            messages.SUCCESS,
        )


# ---------------------------------------------------------------------------
# CircuitEmphasis
# ---------------------------------------------------------------------------


@admin.register(CircuitEmphasis)
class CircuitEmphasisAdmin(admin.ModelAdmin):
    list_display = [
        "circuit",
        "engine",
        "aerodynamics",
        "chassis",
        "suspension",
        "electronics",
        "customized",
        "updated_at",
    ]
    list_filter = ["circuit"]
    search_fields = ["circuit__name"]
    readonly_fields = ["updated_at"]

    @admin.display(description="Personalizado", boolean=True)
    def customized(self, obj: CircuitEmphasis) -> bool:
        return any(
            v != 1.0
            for v in [
                obj.engine,
                obj.aerodynamics,
                obj.chassis,
                obj.suspension,
                obj.electronics,
            ]
        )


# ---------------------------------------------------------------------------
# BalanceOfPerformance
# ---------------------------------------------------------------------------


@admin.register(BalanceOfPerformance)
class BalanceOfPerformanceAdmin(admin.ModelAdmin):
    list_display = [
        "team",
        "season",
        "ballast",
        "restrictor_pct",
        "notes",
        "updated_at",
    ]
    list_filter = ["season"]
    search_fields = ["team__name", "season__name"]
    readonly_fields = ["updated_at"]
