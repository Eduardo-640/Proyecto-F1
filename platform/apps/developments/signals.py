"""
Signals for the developments app.

TeamDevelopment post_save → sync BOPSnapshot
--------------------------------------------
Whenever a TeamDevelopment record is saved the auto-computed BOP breakdown
is recalculated.  The snapshot is only written to the DB when at least one
value has changed (idempotent), so bulk operations that touch many teams
won't generate spurious writes.
"""

from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="developments.TeamDevelopment")
def sync_bop_snapshot(sender, instance, **kwargs):
    """Recalculate and persist BOPSnapshot whenever TeamDevelopment is saved."""
    from . import setup_generator as sg
    from .models import BOPSnapshot

    detail = sg.compute_bop_detail(instance)

    snap, created = BOPSnapshot.objects.get_or_create(
        dev=instance,
        defaults={
            "ballast": detail["ballast"],
            "restrictor_pct": detail["restrictor_pct"],
            "ballast_base_reduction": detail["ballast_base_reduction"],
            "restrictor_base_reduction": detail["restrictor_base_reduction"],
            "synergy_ballast": detail["synergy_ballast"],
            "synergy_restrictor": detail["synergy_restrictor"],
            "active_synergies": detail["active_synergies"],
        },
    )

    if created:
        return  # already populated via defaults above

    # Check if anything changed before hitting the DB
    changed = (
        snap.ballast != detail["ballast"]
        or snap.restrictor_pct != detail["restrictor_pct"]
        or snap.ballast_base_reduction != detail["ballast_base_reduction"]
        or snap.restrictor_base_reduction != detail["restrictor_base_reduction"]
        or snap.synergy_ballast != detail["synergy_ballast"]
        or snap.synergy_restrictor != detail["synergy_restrictor"]
        or snap.active_synergies != detail["active_synergies"]
    )

    if changed:
        snap.ballast = detail["ballast"]
        snap.restrictor_pct = detail["restrictor_pct"]
        snap.ballast_base_reduction = detail["ballast_base_reduction"]
        snap.restrictor_base_reduction = detail["restrictor_base_reduction"]
        snap.synergy_ballast = detail["synergy_ballast"]
        snap.synergy_restrictor = detail["synergy_restrictor"]
        snap.active_synergies = detail["active_synergies"]
        snap.save(
            update_fields=[
                "ballast",
                "restrictor_pct",
                "ballast_base_reduction",
                "restrictor_base_reduction",
                "synergy_ballast",
                "synergy_restrictor",
                "active_synergies",
                "computed_at",
            ]
        )
