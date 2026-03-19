from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Driver
from apps.teams.models import Team


@receiver(post_save, sender=Driver)
def ensure_team_for_driver(sender, instance: Driver, created, **kwargs):
    """When a new Driver is created without a team, create a Team named '<Driver name> Team' and assign it."""
    if not created:
        return

    if instance.team:
        return

    base_name = f"{instance.name} - Team" if instance.name else "Unnamed Team"
    # Prefer existing team that starts with the base pattern (avoid creating duplicates)
    existing = Team.objects.filter(name__istartswith=base_name).first()
    if existing:
        team = existing
    else:
        name = base_name
        suffix = 1
        # ensure unique team name
        while Team.objects.filter(name__iexact=name).exists():
            suffix += 1
            name = f"{base_name} {suffix}"

        team = Team.objects.create(name=name)
    instance.team = team
    instance.save(update_fields=["team"])
