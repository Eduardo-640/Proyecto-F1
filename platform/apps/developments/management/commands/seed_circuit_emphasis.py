"""
Management command: seed_circuit_emphasis

Creates missing ``Circuit`` rows (if they don't exist yet) and then seeds
``CircuitEmphasis`` records from the hardcoded ``CIRCUIT_EMPHASIS`` dict in
``setup_generator.py``.

Usage
-----
    python manage.py seed_circuit_emphasis
    python manage.py seed_circuit_emphasis --update   # overwrite existing emphasis records
    python manage.py seed_circuit_emphasis --dry-run  # show what would be done without saving
"""

from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.developments import setup_generator as sg
from apps.developments.models import CircuitEmphasis
from apps.races.models import Circuit

# ---------------------------------------------------------------------------
# Default circuit catalogue — used when the circuit is not in the DB yet.
# Fields: name, location, laps, length_km
# ---------------------------------------------------------------------------
CIRCUIT_DEFAULTS: dict[str, dict] = {
    "monza": {
        "name": "Autodromo Nazionale di Monza",
        "location": "Monza, Italy",
        "laps": 53,
        "length_km": Decimal("5.79"),
    },
    "hungaroring": {
        "name": "Hungaroring",
        "location": "Budapest, Hungary",
        "laps": 70,
        "length_km": Decimal("4.38"),
    },
    "silverstone": {
        "name": "Silverstone Circuit",
        "location": "Silverstone, United Kingdom",
        "laps": 52,
        "length_km": Decimal("5.89"),
    },
    "imola": {
        "name": "Autodromo Enzo e Dino Ferrari",
        "location": "Imola, Italy",
        "laps": 63,
        "length_km": Decimal("4.91"),
    },
    "spa": {
        "name": "Circuit de Spa-Francorchamps",
        "location": "Stavelot, Belgium",
        "laps": 44,
        "length_km": Decimal("7.00"),
    },
    "barcelona": {
        "name": "Circuit de Barcelona-Catalunya",
        "location": "Montmeló, Spain",
        "laps": 66,
        "length_km": Decimal("4.66"),
    },
}


class Command(BaseCommand):
    help = (
        "Create missing Circuit rows and seed CircuitEmphasis presets "
        "from the hardcoded CIRCUIT_EMPHASIS defaults."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--update",
            action="store_true",
            help="Overwrite values on existing CircuitEmphasis records.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be seeded without writing to the database.",
        )

    def handle(self, *args, **options):
        update = options["update"]
        dry_run = options["dry_run"]

        circuits_created = 0
        emphasis_created = emphasis_updated = emphasis_skipped = 0

        for key, weights in sg.CIRCUIT_EMPHASIS.items():
            # ----------------------------------------------------------------
            # Step 1: ensure Circuit exists — create from CIRCUIT_DEFAULTS if not
            # ----------------------------------------------------------------
            matches = list(Circuit.objects.filter(name__icontains=key))

            if not matches:
                defaults = CIRCUIT_DEFAULTS.get(key)
                if not defaults:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  NO DEFAULTS for '{key}' — add an entry to CIRCUIT_DEFAULTS "
                            "in this command and re-run."
                        )
                    )
                    continue

                if dry_run:
                    self.stdout.write(
                        f"  [dry-run] CREATE Circuit: {defaults['name']} ({defaults['location']})"
                    )
                else:
                    circuit = Circuit.objects.create(**defaults)
                    circuits_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  CREATED Circuit: {circuit.name}")
                    )
                    matches = [circuit]
            else:
                circuit = matches[0]
                if len(matches) > 1:
                    names = ", ".join(str(c) for c in matches)
                    self.stdout.write(
                        self.style.WARNING(
                            f"  AMBIGUOUS '{key}' — {len(matches)} circuits match: {names}. "
                            "Using the first one."
                        )
                    )

            if dry_run:
                # In dry-run we don't have a real circuit object for keys that
                # would be created — skip the emphasis step.
                circuit_name = (
                    CIRCUIT_DEFAULTS.get(key, {}).get("name", key)
                    if not matches
                    else matches[0].name
                )
                exists = (
                    Circuit.objects.filter(name__icontains=key).exists()
                    and CircuitEmphasis.objects.filter(
                        circuit__name__icontains=key
                    ).exists()
                )
                action = "UPDATE" if exists else "CREATE"
                self.stdout.write(
                    f"  [dry-run] {action} CircuitEmphasis for {circuit_name}: "
                    + ", ".join(f"{d}={v}" for d, v in weights.items())
                )
                if exists:
                    emphasis_updated += 1
                else:
                    emphasis_created += 1
                continue

            # ----------------------------------------------------------------
            # Step 2: create or update CircuitEmphasis
            # ----------------------------------------------------------------
            circuit = matches[0]
            exists = CircuitEmphasis.objects.filter(circuit=circuit).exists()

            if exists and not update:
                self.stdout.write(
                    f"  SKIP CircuitEmphasis for {circuit.name} "
                    "(already exists, use --update to overwrite)"
                )
                emphasis_skipped += 1
                continue

            _, was_created = CircuitEmphasis.objects.update_or_create(
                circuit=circuit,
                defaults=weights,
            )

            if was_created:
                emphasis_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  CREATED CircuitEmphasis for {circuit.name}")
                )
            else:
                emphasis_updated += 1
                self.stdout.write(f"  UPDATED CircuitEmphasis for {circuit.name}")

        suffix = " (dry-run, nothing saved)" if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone{suffix}:\n"
                f"  Circuits : {circuits_created} created\n"
                f"  Emphasis : {emphasis_created} created, "
                f"{emphasis_updated} updated, {emphasis_skipped} skipped"
            )
        )
