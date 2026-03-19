from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.teams.models import Team
from apps.seasons.models import Season
from apps.races.models import Circuit
from .constants import MIN_LEVEL, MAX_LEVEL, Department

level_field = lambda: models.PositiveSmallIntegerField(  # noqa: E731
    default=1,
    validators=[MinValueValidator(MIN_LEVEL), MaxValueValidator(MAX_LEVEL)],
)


class TeamDevelopment(models.Model):
    """Current technical development state of a team in a season."""

    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="developments"
    )
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="developments"
    )

    engine = level_field()
    aerodynamics = level_field()
    chassis = level_field()
    suspension = level_field()
    electronics = level_field()

    # Set to True after apply_starting_bonuses() runs for this team+season.
    # Prevents the sponsor bonus from being applied more than once.
    bonuses_applied = models.BooleanField(
        default=False,
        help_text="True once sponsor affinity bonuses have been applied. Prevents double-application.",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["team", "season"]
        verbose_name = "Team Development"
        verbose_name_plural = "Team Developments"

    def __str__(self):
        return f"{self.team} – {self.season}"

    def get_level(self, department: str) -> int:
        return getattr(self, department)


class PurchasedUpgrade(models.Model):
    """History of upgrades purchased by a team."""

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="upgrades")
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="upgrades"
    )
    department = models.CharField(max_length=20, choices=Department.choices)
    previous_level = models.PositiveSmallIntegerField()
    new_level = models.PositiveSmallIntegerField()
    cost = models.PositiveIntegerField()
    applied = models.BooleanField(default=False)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-purchased_at"]
        verbose_name = "Purchased Upgrade"
        verbose_name_plural = "Purchased Upgrades"

    def __str__(self):
        return f"{self.team} – {self.get_department_display()} {self.previous_level}→{self.new_level}"

    def clean(self):
        # Validate cost matches configured pricing for single-level upgrades
        from .setup_service import compute_upgrade_cost

        if self.new_level != self.previous_level + 1:
            raise ValueError("Upgrades must increase level by exactly 1")
        expected = compute_upgrade_cost(self.previous_level, self.new_level)
        if expected and self.cost != expected:
            raise ValueError(
                f"Cost mismatch: expected {expected} for {self.previous_level}->{self.new_level}"
            )


class CarSetupSnapshot(models.Model):
    """Versioned snapshot of a team's car .ini setup for a season.

    Created once as the initial preset and again after every upgrade that
    changes at least one INI parameter.  The full INI text is stored so
    any version can be replayed or diffed.
    """

    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="setup_snapshots"
    )
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="setup_snapshots"
    )
    version = models.PositiveSmallIntegerField()

    # Full .ini text ready to be written to disk
    ini_content = models.TextField()
    # All computed param values — stored for fast diffing without INI parsing
    params_json = models.JSONField(default=dict)
    # Only the params that changed vs the previous version (empty for v1)
    changed_params = models.JSONField(default=dict, blank=True)

    # The upgrade that triggered this version (null = initial preset)
    upgrade = models.OneToOneField(
        "PurchasedUpgrade",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="setup_snapshot",
    )
    # Personality assigned at version 1; propagated to all subsequent versions
    preset_bias = models.CharField(max_length=30, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["team", "season", "version"]
        ordering = ["team", "season", "version"]
        verbose_name = "Car Setup Snapshot"
        verbose_name_plural = "Car Setup Snapshots"

    def __str__(self):
        return f"{self.team} – {self.season} v{self.version} ({self.preset_bias or 'no bias'})"


class CircuitSetup(models.Model):
    """Per-circuit race-weekend setup for a team.

    Built on top of the current ``CarSetupSnapshot`` (development state),
    with driver-chosen overrides for all **tunable** parameters.
    The permanent structural parameters (SPRING_RATE, ROD_LENGTH) are
    always taken from the development snapshot and cannot be overridden here.
    """

    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="circuit_setups"
    )
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="circuit_setups"
    )
    circuit = models.ForeignKey(
        Circuit, on_delete=models.CASCADE, related_name="circuit_setups"
    )
    # The development snapshot this setup is based on
    base_snapshot = models.ForeignKey(
        CarSetupSnapshot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="circuit_setups",
    )
    # Driver-set overrides: {param_name: value} — only tunable params accepted
    tunable_overrides = models.JSONField(
        default=dict,
        blank=True,
        help_text="Driver-chosen values for tunable parameters (aero, diff, dampers…)",
    )
    # Final rendered INI ready to write to disk
    ini_content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["team", "season", "circuit"]
        ordering = ["team", "season", "circuit"]
        verbose_name = "Circuit Setup"
        verbose_name_plural = "Circuit Setups"

    def __str__(self):
        return f"{self.team} – {self.circuit} ({self.season})"


class BalanceOfPerformance(models.Model):
    """Admin-managed Balance of Performance (BOP) entry for a team in a season.

    Ballast and restrictor are written as extra INI sections (BALLAST /
    RESTRICTOR) appended to any generated setup file for that team.
    These are intentionally kept outside the development algorithm so
    the admin retains full manual control over competitive equalisation.
    """

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="bop_entries")
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="bop_entries"
    )
    # Positive = heavier (handicap); negative = weight reduction (bonus)
    ballast = models.IntegerField(
        default=0,
        help_text="Ballast in kg. Positive = heavier (handicap), negative = lighter (bonus).",
    )
    # 0 = no restrictor; 1–100 = percentage of power reduction simulated
    restrictor_pct = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        help_text="Engine restrictor as % power reduction (0 = none).",
    )
    notes = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["team", "season"]
        verbose_name = "Balance of Performance"
        verbose_name_plural = "Balance of Performance Entries"

    def __str__(self):
        return (
            f"{self.team} – {self.season} "
            f"(ballast={self.ballast:+d}kg, restrictor={self.restrictor_pct}%)"
        )

    @property
    def as_bop_overrides(self) -> dict[str, int]:
        """Return the dict expected by ``render_setup_ini(bop_overrides=...)``."""
        overrides: dict[str, int] = {}
        if self.ballast != 0:
            overrides["BALLAST"] = self.ballast
        if self.restrictor_pct > 0:
            overrides["RESTRICTOR"] = self.restrictor_pct
        return overrides


class CircuitEmphasis(models.Model):
    """Per-circuit department emphasis weights, editable in the admin.

    These multipliers are applied over the base LEVEL_PERF modifier during
    setup generation.  Values > 1 reward that department more at this circuit;
    values < 1 discount it.  Defaults are seeded from the hardcoded
    ``CIRCUIT_EMPHASIS`` dict in ``setup_generator.py`` via the
    ``seed_circuit_emphasis`` management command.
    """

    circuit = models.OneToOneField(
        Circuit,
        on_delete=models.CASCADE,
        related_name="emphasis",
    )
    engine = models.FloatField(default=1.0)
    aerodynamics = models.FloatField(default=1.0)
    chassis = models.FloatField(default=1.0)
    suspension = models.FloatField(default=1.0)
    electronics = models.FloatField(default=1.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["circuit__name"]
        verbose_name = "Circuit Emphasis"
        verbose_name_plural = "Circuit Emphasis Presets"

    def __str__(self):
        return f"{self.circuit} — emphasis"

    def as_dict(self) -> dict[str, float]:
        """Return the emphasis as the dict expected by ``compute_modifiers``."""
        return {
            "engine": self.engine,
            "aerodynamics": self.aerodynamics,
            "chassis": self.chassis,
            "suspension": self.suspension,
            "electronics": self.electronics,
        }


class BOPSnapshot(models.Model):
    """Persisted auto-computed BOP breakdown, always in sync with TeamDevelopment.

    Created and updated automatically by the ``post_save`` signal on
    ``TeamDevelopment`` — only written when the computed values differ from
    what is already stored (idempotent).

    Ballast and restrictor start at 200 kg / 100% and are progressively
    reduced by department levels (weighted) and synergy bonuses.
    """

    dev = models.OneToOneField(
        TeamDevelopment,
        on_delete=models.CASCADE,
        related_name="bop_snapshot",
        verbose_name="Development",
    )

    # Final computed values (what the INI gets when no manual BOP record exists)
    ballast = models.PositiveSmallIntegerField(default=200)
    restrictor_pct = models.PositiveSmallIntegerField(default=100)

    # Breakdown components
    ballast_base_reduction = models.PositiveSmallIntegerField(default=0)
    restrictor_base_reduction = models.PositiveSmallIntegerField(default=0)
    synergy_ballast = models.PositiveSmallIntegerField(default=0)
    synergy_restrictor = models.PositiveSmallIntegerField(default=0)

    # Active synergy pairs — list of {label, ballast, restrictor} dicts
    active_synergies = models.JSONField(default=list)

    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "BOP Snapshot"
        verbose_name_plural = "BOP Snapshots"

    def __str__(self):
        return f"{self.dev} — auto BOP: {self.ballast} kg / {self.restrictor_pct}%"


class AccionMasiva(models.Model):
    """Centralized bulk operation executor for the development system.

    Each record represents a single batch action.  On first save the admin
    executes it immediately and records the result in ``result_log``.
    Leave ``team`` blank to target **all** teams in the season.
    """

    class ActionType(models.TextChoices):
        INIT_PRESETS = "init_presets", "Generate Initial Setup Presets"
        APPLY_BONUSES = "apply_bonuses", "Apply Sponsor Affinity Bonuses"
        GENERATE_CIRCUIT_SETUPS = "generate_circuit_setups", "Generate Circuit Setups"
        SYNC_BOP = "sync_bop", "Sync BOP from Development Levels"
        RESET_CONFIGS = "reset_configs", "Reset Team Configurations"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        OK = "ok", "Completed OK"
        ERROR = "error", "Completed with Errors"

    action_type = models.CharField(
        max_length=40,
        choices=ActionType.choices,
        verbose_name="Action",
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="acciones",
    )
    # Null = apply to ALL teams in the season
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acciones",
        help_text="Leave blank to apply to ALL teams in the season.",
    )
    # Only for INIT_PRESETS
    bias = models.CharField(
        max_length=30,
        blank=True,
        help_text=(
            "Setup personality: speed, cornering, consistency, technical, "
            "raw_power, balanced. Leave blank for random. "
            "Only used for 'Generate Initial Setup Presets'."
        ),
    )
    # Only for GENERATE_CIRCUIT_SETUPS
    circuit = models.ForeignKey(
        Circuit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acciones",
        help_text="Only required for 'Generate Circuit Setups'.",
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        editable=False,
    )
    result_log = models.TextField(blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Acción Masiva"
        verbose_name_plural = "Acciones Masivas"

    def __str__(self):
        team_label = str(self.team) if self.team else "all teams"
        return f"{self.get_action_type_display()} – {self.season} – {team_label}"

    def execute(self) -> None:
        """Execute the selected bulk action and persist a result log.

        This method is idempotent in the sense that it records status and
        avoids partial commits by wrapping each top-level loop in a
        transaction. Errors are captured into `result_log` and the `status`
        field is updated accordingly.
        """
        from django.utils import timezone
        from django.db import transaction
        from io import StringIO

        from . import setup_service as service
        from . import setup_generator as sg

        buf = StringIO()
        attempted = 0
        successes = 0
        errors = 0

        try:
            with transaction.atomic():
                from apps.teams.models import Team as _Team

                targets = (
                    [self.team]
                    if self.team is not None
                    else list(_Team.objects.filter(active=True))
                )

                for team in targets:
                    attempted += 1
                    try:
                        if self.action_type == self.ActionType.INIT_PRESETS:
                            # Ensure TeamDevelopment exists
                            dev, created = (
                                service.TeamDevelopment.objects.get_or_create(
                                    team=team, season=self.season
                                )
                            )
                            # Apply starting bonuses then generate v1 preset if missing
                            applied = service.apply_starting_bonuses(dev)
                            if not service.CarSetupSnapshot.objects.filter(
                                team=team, season=self.season
                            ).exists():
                                service.generate_initial_preset(
                                    dev, bias=self.bias or None
                                )
                            buf.write(f"{team}: init_presets ok (bonuses={applied})\n")

                        elif self.action_type == self.ActionType.APPLY_BONUSES:
                            dev, _ = service.TeamDevelopment.objects.get_or_create(
                                team=team, season=self.season
                            )
                            applied = service.apply_starting_bonuses(dev)
                            buf.write(f"{team}: apply_bonuses -> {applied}\n")

                        elif (
                            self.action_type == self.ActionType.GENERATE_CIRCUIT_SETUPS
                        ):
                            if not self.circuit:
                                raise ValueError(
                                    "Circuit is required for generate_circuit_setups"
                                )
                            dev, _ = service.TeamDevelopment.objects.get_or_create(
                                team=team, season=self.season
                            )
                            setup = service.generate_circuit_setup(dev, self.circuit)
                            buf.write(f"{team}: generated circuit setup {setup}\n")

                        elif self.action_type == self.ActionType.SYNC_BOP:
                            # Compute auto BOP and persist BOPSnapshot
                            dev, _ = service.TeamDevelopment.objects.get_or_create(
                                team=team, season=self.season
                            )
                            auto = sg.compute_bop(dev)
                            from .models import BOPSnapshot

                            BOPSnapshot.objects.update_or_create(
                                dev=dev,
                                defaults={
                                    "ballast": auto["ballast"],
                                    "restrictor_pct": auto["restrictor_pct"],
                                    "ballast_base_reduction": auto.get(
                                        "ballast_base_reduction", 0
                                    ),
                                    "restrictor_base_reduction": auto.get(
                                        "restrictor_base_reduction", 0
                                    ),
                                    "synergy_ballast": auto.get("synergy_ballast", 0),
                                    "synergy_restrictor": auto.get(
                                        "synergy_restrictor", 0
                                    ),
                                    "active_synergies": auto.get(
                                        "active_synergies", []
                                    ),
                                },
                            )
                            buf.write(f"{team}: synced BOP {auto}\n")

                        elif self.action_type == self.ActionType.RESET_CONFIGS:
                            # Reset all generated/derived configuration for the team
                            # - Delete snapshots, upgrades, circuit setups, BOP
                            # - Reset TeamDevelopment levels to MIN_LEVEL and clear bonuses_applied
                            from .constants import MIN_LEVEL

                            # Ensure TeamDevelopment exists
                            dev, _ = service.TeamDevelopment.objects.get_or_create(
                                team=team, season=self.season
                            )

                            # Delete generated records for this team+season
                            deleted_snapshots = CarSetupSnapshot.objects.filter(
                                team=team, season=self.season
                            ).delete()
                            deleted_upgrades = PurchasedUpgrade.objects.filter(
                                team=team, season=self.season
                            ).delete()
                            deleted_circuit_setups = CircuitSetup.objects.filter(
                                team=team, season=self.season
                            ).delete()
                            deleted_bop = BalanceOfPerformance.objects.filter(
                                team=team, season=self.season
                            ).delete()

                            # Reset development levels and bonuses flag
                            fields_updated = []
                            for dept in ("engine", "aerodynamics", "chassis", "suspension", "electronics"):
                                if getattr(dev, dept) != MIN_LEVEL:
                                    setattr(dev, dept, MIN_LEVEL)
                                    fields_updated.append(dept)

                            if dev.bonuses_applied:
                                dev.bonuses_applied = False
                                fields_updated.append("bonuses_applied")

                            if fields_updated:
                                dev.save(update_fields=fields_updated + ["updated_at"])

                            buf.write(
                                f"{team}: reset_configs -> snapshots={deleted_snapshots[0]}, upgrades={deleted_upgrades[0]}, circuit_setups={deleted_circuit_setups[0]}, bop={deleted_bop[0]}, dev_fields_reset={fields_updated}\n"
                            )

                        else:
                            raise ValueError(f"Unknown action: {self.action_type}")

                        successes += 1
                    except Exception as e:
                        errors += 1
                        import traceback

                        buf.write(f"{team}: ERROR: {e}\n")
                        buf.write(traceback.format_exc())

            # If we reach here the transaction committed for all teams
            self.status = self.Status.OK
        except Exception as e:
            # Top-level failure
            self.status = self.Status.ERROR
            buf.write(f"Top-level error: {e}\n")
            import traceback

            buf.write(traceback.format_exc())

        self.result_log = buf.getvalue()
        self.executed_at = timezone.now()
        # Persist status/result_log
        super().save(update_fields=["status", "result_log", "executed_at"])  # type: ignore[arg-type]

    def save(self, *args, **kwargs):
        # Detect creation: call super to obtain pk, then execute immediately
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.status == self.Status.PENDING:
            try:
                self.execute()
            except Exception:
                # execute() already records errors into result_log/status
                pass
