from django.apps import AppConfig


class DevelopmentsConfig(AppConfig):
    name = "apps.developments"
    label = "developments"
    verbose_name = "Developments"

    def ready(self):
        import apps.developments.signals  # noqa: F401
