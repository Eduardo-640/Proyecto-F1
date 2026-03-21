from __future__ import annotations
import csv
import json
import random
import os
from pathlib import Path
from typing import Dict, List

from django.core.management.base import BaseCommand


CATEGORIES = [
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


def parse_int(v, default=0):
    try:
        return int(v)
    except Exception:
        return default


class Command(BaseCommand):
    help = "Genera un fixture JSON de sponsors a partir de un CSV o plantillas predefinidas."

    def add_arguments(self, parser):
        parser.add_argument("--csv", dest="csv", help="Ruta al CSV de sponsors")
        parser.add_argument(
            "--out",
            dest="out",
            help="Ruta de salida JSON (fixture)",
            default="platform/apps/teams/fixtures/sponsors_template.json",
        )
        parser.add_argument(
            "--template-csv",
            action="store_true",
            dest="template_csv",
            help="Escribe un CSV de plantilla editable en platform/apps/teams/fixtures/sponsors_template.csv",
        )
        parser.add_argument(
            "--random-count",
            dest="random_count",
            type=int,
            help="Genera N sponsors aleatorios en vez de leer CSV",
        )
        parser.add_argument(
            "--affinity-total",
            dest="affinity_total",
            type=int,
            default=1,
            help="Número total de puntos positivos (affinity) por sponsor (excluyendo money).",
        )

    def handle(self, *args, **options):
        out_path = Path(options["out"]).resolve()

        # Determine fixtures directory robustly: prefer the app-relative fixtures folder
        # based on this command file location to avoid duplicated 'platform/platform' paths.
        cmd_file = Path(__file__).resolve()
        apps_idx = str(cmd_file).find(os.path.join("apps", "teams"))
        if apps_idx != -1:
            fixtures_dir = (
                Path(str(cmd_file)[:apps_idx]) / "apps" / "teams" / "fixtures"
            )
        else:
            fixtures_dir = out_path.parent
        fixtures_dir.mkdir(parents=True, exist_ok=True)

        # configurable total of positive affinity points per sponsor (excl. money)
        self.affinity_total = int(options.get("affinity_total", 1))

        if options.get("template_csv"):
            csv_path = fixtures_dir / "sponsors_template.csv"
            self._write_csv_template(csv_path)
            self.stdout.write(self.style.SUCCESS(f"Template CSV escrito: {csv_path}"))
            return

        sponsors: List[Dict] = []
        if options.get("csv"):
            raw = options["csv"]
            candidates = []
            # direct path as given
            candidates.append(Path(raw))
            # relative to current working directory
            candidates.append(Path.cwd() / raw)
            # relative to detected fixtures dir
            candidates.append(fixtures_dir / Path(raw).name)
            # try stripping a leading 'platform/' prefix if present
            if raw.startswith("platform/") or raw.startswith("platform\\"):
                stripped = raw.split("/", 1)[1] if "/" in raw else raw.split("\\", 1)[1]
                candidates.append(Path(stripped))
                candidates.append(Path.cwd() / stripped)
                candidates.append(fixtures_dir / Path(stripped).name)

            csv_path = None
            for p in candidates:
                try:
                    p_res = p.resolve()
                except Exception:
                    p_res = p
                if p_res.exists():
                    csv_path = p_res
                    break

            if csv_path is None:
                self.stderr.write(f"CSV no encontrado: {raw}")
                return

            sponsors = self._read_from_csv(csv_path)
        elif options.get("random_count"):
            sponsors = self._generate_random(options["random_count"])  # type: ignore
        else:
            self.stderr.write(
                "Especifique --csv PATH o --random-count N o --template-csv"
            )
            return

        fixtures = self._build_fixtures(sponsors)
        final_out = fixtures_dir / out_path.name
        final_out.write_text(json.dumps(fixtures, indent=2, ensure_ascii=False))
        self.stdout.write(self.style.SUCCESS(f"Fixture JSON generado: {final_out}"))

    def _write_csv_template(self, path: Path):
        headers = [
            "name",
            "description",
            "base_bonus",
            "is_main",
            "active",
            # affinities: money then categories
        ] + CATEGORIES
        sample = [
            [
                "Aceite Rápido",
                "Lubricantes que favorecen motor, penalizan electrónica",
                "6500",
                "false",
                "true",
            ]
        ]
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(headers)
            for row in sample:
                # append zeros for each category column
                writer.writerow(row + ["0"] * len(CATEGORIES))

    def _read_from_csv(self, path: Path) -> List[Dict]:
        sponsors: List[Dict] = []
        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for i, row in enumerate(reader, start=1):
                sponsor = {
                    "name": row.get("name", "Sponsor %d" % i).strip(),
                    "description": row.get("description", "").strip(),
                    "base_bonus": max(0, parse_int(row.get("base_bonus"), 0)),
                    "is_main": row.get("is_main", "false").lower()
                    in ("1", "true", "yes"),
                    "active": row.get("active", "true").lower() in ("1", "true", "yes"),
                    "conditions": {},
                }
                for cat in CATEGORIES:
                    sponsor["conditions"][cat] = parse_int(row.get(cat, 0), 0)

                # normalize values: non-money categories -> -1/0/+1; money kept as integer (>=1)
                for cat, val in list(sponsor["conditions"].items()):
                    if cat == "money":
                        sponsor["conditions"][cat] = (
                            max(1, int(val)) if int(val) != 0 else 1
                        )
                    else:
                        v = int(val)
                        sponsor["conditions"][cat] = (
                            0 if v == 0 else (1 if v > 0 else -1)
                        )

                # enforce exact number of positive affinity points among non-money categories
                cats_no_money = [c for c in CATEGORIES if c != "money"]
                positives = [
                    c for c in cats_no_money if sponsor["conditions"].get(c, 0) > 0
                ]
                # add positives if too few
                if len(positives) < self.affinity_total:
                    choices = [
                        c for c in cats_no_money if sponsor["conditions"].get(c, 0) == 0
                    ]
                    while len(positives) < self.affinity_total and choices:
                        pick = random.choice(choices)
                        sponsor["conditions"][pick] = 1
                        positives.append(pick)
                        choices.remove(pick)
                # reduce positives if too many
                if len(positives) > self.affinity_total:
                    to_remove = len(positives) - self.affinity_total
                    for _ in range(to_remove):
                        rem = random.choice(positives)
                        sponsor["conditions"][rem] = 0
                        positives.remove(rem)

                # ensure at least one negative exists among non-money
                negatives = [
                    c for c in cats_no_money if sponsor["conditions"].get(c, 0) < 0
                ]
                if not negatives:
                    zeros = [
                        c for c in cats_no_money if sponsor["conditions"].get(c, 0) == 0
                    ]
                    if zeros:
                        sponsor["conditions"][random.choice(zeros)] = -1
                    else:
                        # fallback: turn one positive into negative
                        if positives:
                            flip = random.choice(positives)
                            sponsor["conditions"][flip] = -1

                # validation / auto-fill rules
                # ensure money exists
                if sponsor["conditions"].get("money", 0) == 0:
                    sponsor["conditions"]["money"] = 1

                # ensure at least one positive and one negative across categories (excluding money)
                cats_no_money = [c for c in CATEGORIES if c != "money"]
                positives = any(
                    sponsor["conditions"].get(c, 0) > 0 for c in cats_no_money
                )
                negatives = any(
                    sponsor["conditions"].get(c, 0) < 0 for c in cats_no_money
                )
                if not positives:
                    # pick a random category to boost
                    sponsor["conditions"][random.choice(cats_no_money)] = 1
                if not negatives:
                    # pick a different category to penalize
                    choices = [
                        c for c in cats_no_money if sponsor["conditions"].get(c, 0) == 0
                    ]
                    if not choices:
                        choices = cats_no_money
                    sponsor["conditions"][random.choice(choices)] = -1

                sponsors.append(sponsor)
        return sponsors

    def _generate_random(self, n: int) -> List[Dict]:
        names = [
            "Aceite Rápido",
            "AeroPlus",
            "Chasis&Cía",
            "Electronía Nova",
            "Suspensión S.A.",
            "DineroRápido",
            "Composites del Sur",
            "Neumáticos Rojos",
            "MediaMóvil",
            "Taller Ñ",
            "TurboFicción",
            "EcoMoto",
            "Bits&Bytes",
            "Hotel Gran Parada",
            "Banco del Circuito",
            "Ingenio Láser",
        ]
        sponsors: List[Dict] = []
        for i in range(n):
            name = names[i % len(names)] + (
                f" {i//len(names)+1}" if i >= len(names) else ""
            )
            base = random.choice([2000, 3000, 5000, 7000, 9000, 12000])
            conds = {c: 0 for c in CATEGORIES}
            # money positive (keep value >=1, may be >1)
            conds["money"] = random.choice([1, 1, 2, 3])
            # pick exactly self.affinity_total positives
            available = [c for c in CATEGORIES if c != "money"]
            k = min(self.affinity_total, len(available))
            pos_cats = random.sample(available, k=k)
            for pc in pos_cats:
                conds[pc] = 1
            # pick one penalty (negative) in a different category if possible
            neg_choices = [c for c in available if c not in pos_cats]
            if not neg_choices:
                neg_choices = [c for c in available]
            neg_cat = random.choice(neg_choices)
            conds[neg_cat] = -1

            sponsors.append(
                {
                    "name": name,
                    "description": f"Patrocinador generado: {name}",
                    "base_bonus": base,
                    "is_main": False,
                    "active": True,
                    "conditions": conds,
                }
            )
        return sponsors

    def _build_fixtures(self, sponsors: List[Dict]) -> List[Dict]:
        fixtures: List[Dict] = []
        sponsor_pk = 1
        cond_pk = 1001
        for s in sponsors:
            fixtures.append(
                {
                    "model": "teams.sponsor",
                    "pk": sponsor_pk,
                    "fields": {
                        "team": None,
                        "name": s["name"],
                        "description": s.get("description", ""),
                        "is_main": s.get("is_main", False),
                        "base_bonus": int(s.get("base_bonus", 0)),
                        "total_score": int(
                            sum(
                                v
                                for k, v in s.get("conditions", {}).items()
                                if k != "money"
                            )
                        ),
                        "active": bool(s.get("active", True)),
                    },
                }
            )
            for cat, val in s.get("conditions", {}).items():
                # ensure every category is present in fixtures (including 0)
                if cat == "money":
                    typ = "money" if int(val) != 0 else "neutral"
                else:
                    if int(val) == 0:
                        typ = "neutral"
                    else:
                        typ = "affinity" if int(val) > 0 else "penalty"

                fixtures.append(
                    {
                        "model": "teams.sponsorcondition",
                        "pk": cond_pk,
                        "fields": {
                            "sponsor": sponsor_pk,
                            "type": typ,
                            "category": cat,
                            "value": int(val),
                            "description": f"Auto: {cat} {val}",
                        },
                    }
                )
                cond_pk += 1
            sponsor_pk += 1
        return fixtures
