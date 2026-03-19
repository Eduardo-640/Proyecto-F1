from django.apps import AppConfig


class DriversConfig(AppConfig):
    name = "apps.drivers"
    label = "drivers"
    verbose_name = "Drivers"

    def ready(self):
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
