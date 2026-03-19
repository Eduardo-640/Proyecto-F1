from django.apps import AppConfig


class RacesConfig(AppConfig):
    name = "apps.races"
    label = "races"
    verbose_name = "Races"

    def ready(self):
        # import signals to ensure they are registered
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
