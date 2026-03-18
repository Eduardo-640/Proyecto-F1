"""
Django admin configuration for the developments app.

Bulk operations are managed through **AccionMasiva** — a single entry point
that targets one season (and, optionally, one team) and logs results.
Individual model admins retain lightweight save_model overrides for the
operations that are naturally triggered by a single-object save.
"""

from __future__ import annotations

import traceback

from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    AccionMasiva,
    BalanceOfPerformance,
    BOPSnapshot,
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

        # ------------------------------------------------------------------ #
        # SYNC_BOP — create / update BalanceOfPerformance from dev levels    #
        # ------------------------------------------------------------------ #
        elif accion.action_type == AccionMasiva.ActionType.SYNC_BOP:
            for dev in devs:
                try:
                    auto = sg.compute_bop(dev)
                    bop, created = BalanceOfPerformance.objects.update_or_create(
                        team=dev.team,
                        season=dev.season,
                        defaults={
                            "ballast": auto["ballast"],
                            "restrictor_pct": auto["restrictor_pct"],
                        },
                    )
                    verb = "created" if created else "updated"
                    lines.append(
                        f"OK   {dev.team}: BOP {verb} "
                        f"(ballast={auto['ballast']}kg, restrictor={auto['restrictor_pct']}%)."
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
        "auto_bop_summary",
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

    @admin.display(description="Auto-BOP")
    def auto_bop_summary(self, obj: TeamDevelopment) -> str:
        try:
            snap = obj.bop_snapshot
            syn_count = len(snap.active_synergies)
            syn_note = f" +{syn_count}syn" if syn_count else ""
            return f"{snap.ballast}kg / {snap.restrictor_pct}%{syn_note}"
        except BOPSnapshot.DoesNotExist:
            return "— (no snapshot)"
        except Exception:
            return "—"


# ---------------------------------------------------------------------------
# PurchasedUpgrade
# ---------------------------------------------------------------------------

from .constants import MAX_LEVEL, MIN_LEVEL


class PurchasedUpgradeForm(forms.ModelForm):
    """Form that hides previous/new level on creation (auto-filled by save_model)."""

    class Meta:
        model = PurchasedUpgrade
        fields = ["team", "season", "department", "cost", "applied"]


@admin.register(PurchasedUpgrade)
class PurchasedUpgradeAdmin(admin.ModelAdmin):
    list_display = [
        "team",
        "season",
        "department",
        "level_arrow",
        "cost",
        "applied",
        "purchased_at",
    ]
    list_filter = ["season", "department", "applied"]
    search_fields = ["team__name", "season__name", "department"]

    def get_form(self, request, obj=None, **kwargs):
        # On add (obj is None) use the simplified form; on change use full auto form.
        if obj is None:
            kwargs["form"] = PurchasedUpgradeForm
        return super().get_form(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            # Editing an existing record — show computed fields as read-only.
            return [
                "team",
                "season",
                "department",
                "previous_level",
                "new_level",
                "purchased_at",
                "current_levels_panel",
            ]
        return ["current_levels_panel"]

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return [
                (
                    "Upgrade",
                    {
                        "fields": ["team", "season", "department", "cost", "applied"],
                        "description": (
                            "Selecciona equipo, temporada y departamento. "
                            "<strong>previous_level y new_level se calculan automáticamente</strong> "
                            "desde el estado actual del equipo."
                        ),
                    },
                ),
                (
                    "Niveles actuales del equipo",
                    {
                        "fields": ["current_levels_panel"],
                        "classes": ["collapse"],
                        "description": "Disponible tras seleccionar equipo + temporada.",
                    },
                ),
            ]
        return [
            (
                "Upgrade",
                {
                    "fields": [
                        "team",
                        "season",
                        "department",
                        "previous_level",
                        "new_level",
                        "cost",
                        "applied",
                        "purchased_at",
                    ],
                },
            ),
            (
                "Niveles actuales del equipo",
                {"fields": ["current_levels_panel"]},
            ),
        ]

    @admin.display(description="Nivel")
    def level_arrow(self, obj: PurchasedUpgrade) -> str:
        return f"{obj.previous_level} → {obj.new_level}"

    @admin.display(description="Niveles actuales (dev)")
    def current_levels_panel(self, obj: PurchasedUpgrade) -> str:
        try:
            dev = TeamDevelopment.objects.get(team=obj.team, season=obj.season)
        except TeamDevelopment.DoesNotExist:
            return "— No TeamDevelopment encontrado"
        depts = ("engine", "aerodynamics", "chassis", "suspension", "electronics")
        parts = []
        for d in depts:
            lvl = getattr(dev, d)
            label = d.capitalize()
            highlight = (
                " style='font-weight:bold;color:#2a7ae2'" if d == obj.department else ""
            )
            parts.append(f"<span{highlight}>{label}: {lvl}</span>")
        return format_html(" &nbsp;|&nbsp; ".join(parts))

    def save_model(self, request, obj, form, change):
        """Auto-fill previous/new level and evolve car setup when applied."""
        # ── Auto-fill levels on creation ──────────────────────────────────
        if not change:
            try:
                dev = TeamDevelopment.objects.get(team=obj.team, season=obj.season)
            except TeamDevelopment.DoesNotExist:
                self.message_user(
                    request,
                    f"No TeamDevelopment para {obj.team} en {obj.season}. "
                    "Créalo primero.",
                    messages.ERROR,
                )
                return

            current = dev.get_level(obj.department)
            if current >= MAX_LEVEL:
                self.message_user(
                    request,
                    f"{obj.team} ya está en nivel máximo ({MAX_LEVEL}) "
                    f"en {obj.department}. No se puede mejorar más.",
                    messages.ERROR,
                )
                return

            obj.previous_level = current
            obj.new_level = current + 1

        # ── Validate level continuity (safety net for edits) ──────────────
        if obj.new_level != obj.previous_level + 1:
            self.message_user(
                request,
                f"Upgrade inválido: los niveles deben subir de 1 en 1 "
                f"({obj.previous_level} → {obj.new_level} no está permitido).",
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

        # ── Apply the upgrade to TeamDevelopment + evolve snapshot ────────
        try:
            dev = TeamDevelopment.objects.get(team=obj.team, season=obj.season)
        except TeamDevelopment.DoesNotExist:
            self.message_user(
                request,
                f"No TeamDevelopment para {obj.team} en {obj.season}.",
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
                f"Upgrade guardado pero la evolución del setup falló: {exc}",
                messages.ERROR,
            )
            return

        if snapshot:
            changed_keys = list(snapshot.changed_params)
            self.message_user(
                request,
                f"Setup actualizado → v{snapshot.version} "
                f"({len(changed_keys)} parámetro(s) cambiado(s): "
                f"{', '.join(changed_keys[:6])}"
                f"{'…' if len(changed_keys) > 6 else ''})."
                " Recuerda regenerar los Circuit Setups si quieres aplicarlo al fin de semana.",
                messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "Upgrade aplicado, pero ningún parámetro INI cambió "
                "(los umbrales de sinergia aún no se han alcanzado). "
                "Regenera los Circuit Setups si quieres reflejar el cambio de nivel.",
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
        "auto_ballast",
        "auto_restrictor",
        "is_overridden",
        "notes",
        "updated_at",
    ]
    list_filter = ["season"]
    search_fields = ["team__name", "season__name"]
    readonly_fields = ["updated_at", "bop_breakdown_panel"]

    fieldsets = [
        (
            "Valores aplicados",
            {
                "fields": [
                    "team",
                    "season",
                    "ballast",
                    "restrictor_pct",
                    "notes",
                    "updated_at",
                ],
                "description": (
                    "Punto de partida siempre: <strong>200 kg / 100%</strong>. "
                    "Usa <em>AccionMasiva → Sync BOP</em> para rellenar automáticamente "
                    "según los niveles actuales, o edita manualmente para sobrescribir. "
                    "El desglose de abajo se recalcula en tiempo real — no se almacena "
                    "porque siempre se puede derivar de los niveles de desarrollo."
                ),
            },
        ),
        (
            "Desglose automático en tiempo real",
            {
                "fields": ["bop_breakdown_panel"],
                "description": (
                    "Calculado al momento desde <em>TeamDevelopment</em>. "
                    "Si difiere de los valores aplicados arriba es porque se editaron manualmente."
                ),
            },
        ),
    ]

    @admin.display(description="Auto Ballast")
    def auto_ballast(self, obj: BalanceOfPerformance) -> str:
        try:
            snap = TeamDevelopment.objects.get(
                team=obj.team, season=obj.season
            ).bop_snapshot
            return f"{snap.ballast} kg"
        except Exception:
            return "—"

    @admin.display(description="Auto Restrictor")
    def auto_restrictor(self, obj: BalanceOfPerformance) -> str:
        try:
            snap = TeamDevelopment.objects.get(
                team=obj.team, season=obj.season
            ).bop_snapshot
            return f"{snap.restrictor_pct} %"
        except Exception:
            return "—"

    @admin.display(description="Manual?", boolean=True)
    def is_overridden(self, obj: BalanceOfPerformance) -> bool:
        try:
            snap = TeamDevelopment.objects.get(
                team=obj.team, season=obj.season
            ).bop_snapshot
            return (
                obj.ballast != snap.ballast or obj.restrictor_pct != snap.restrictor_pct
            )
        except Exception:
            return False

    @admin.display(description="Desglose BOP automático")
    def bop_breakdown_panel(self, obj: BalanceOfPerformance) -> str:
        try:
            dev = TeamDevelopment.objects.get(team=obj.team, season=obj.season)
            snap = dev.bop_snapshot
        except TeamDevelopment.DoesNotExist:
            return format_html(
                "<em>Sin TeamDevelopment para este equipo + temporada.</em>"
            )
        except BOPSnapshot.DoesNotExist:
            return format_html(
                "<em>Sin BOP Snapshot — guarda el TeamDevelopment una vez para generarlo.</em>"
            )
        except Exception as exc:
            return format_html("<em>Error: {}</em>", str(exc))

        rows = [
            f"<strong>Ballast auto: {snap.ballast} kg</strong>"
            f" &nbsp;=&nbsp; 200 − {snap.ballast_base_reduction} (niveles)"
            f" − {snap.synergy_ballast} (sinergias)",
            f"<strong>Restrictor auto: {snap.restrictor_pct} %</strong>"
            f" &nbsp;=&nbsp; 100 − {snap.restrictor_base_reduction} (niveles)"
            f" − {snap.synergy_restrictor} (sinergias)",
            f"<em style='color:#888'>Calculado: {snap.computed_at.strftime('%d/%m/%Y %H:%M')}</em>",
            "",
        ]

        if snap.active_synergies:
            rows.append("<strong>Sinergias activas:</strong>")
            for s in snap.active_synergies:
                rows.append(
                    f"&nbsp;&nbsp;• {s['label']}: &minus;{s['ballast']} kg / &minus;{s['restrictor']}%"
                )
        else:
            rows.append(
                "<em>Sin sinergias activas — sube Motor o Chasis para desbloquearlas.</em>"
            )

        if obj.ballast != snap.ballast or obj.restrictor_pct != snap.restrictor_pct:
            rows.extend(
                [
                    "",
                    "<span style='color:#e67e00'>&#9888; Valores manuales difieren del auto: "
                    f"ballast={obj.ballast:+d} kg (auto={snap.ballast}), "
                    f"restrictor={obj.restrictor_pct}% (auto={snap.restrictor_pct}%)</span>",
                ]
            )

        return format_html("<br>".join(rows))


# ---------------------------------------------------------------------------
# BOPSnapshot
# ---------------------------------------------------------------------------


@admin.register(BOPSnapshot)
class BOPSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        "dev",
        "ballast",
        "restrictor_pct",
        "ballast_base_reduction",
        "restrictor_base_reduction",
        "synergy_ballast",
        "synergy_restrictor",
        "active_synergies_summary",
        "computed_at",
    ]
    list_filter = ["dev__season"]
    search_fields = ["dev__team__name", "dev__season__name"]
    readonly_fields = [
        "dev",
        "ballast",
        "restrictor_pct",
        "ballast_base_reduction",
        "restrictor_base_reduction",
        "synergy_ballast",
        "synergy_restrictor",
        "active_synergies",
        "computed_at",
    ]

    fieldsets = [
        (
            "Resultado",
            {
                "fields": ["dev", "ballast", "restrictor_pct", "computed_at"],
                "description": (
                    "Valores calculados automáticamente desde los niveles de desarrollo. "
                    "Se actualizan solos cada vez que cambia <em>TeamDevelopment</em>."
                ),
            },
        ),
        (
            "Desglose",
            {
                "fields": [
                    "ballast_base_reduction",
                    "restrictor_base_reduction",
                    "synergy_ballast",
                    "synergy_restrictor",
                    "active_synergies",
                ],
            },
        ),
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="Sinergias activas")
    def active_synergies_summary(self, obj: BOPSnapshot) -> str:
        if not obj.active_synergies:
            return "—"
        return ", ".join(s["label"] for s in obj.active_synergies)
