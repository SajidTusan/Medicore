from django.apps import AppConfig


class MedicalRecordsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.medical_records"

    def ready(self):
        try:
            from . import signals  # noqa: F401
        except ImportError:
            pass