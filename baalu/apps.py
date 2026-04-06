from django.apps import AppConfig


class BaaluAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'baalu'

    def ready(self):
        from baalu import signals  # Инициализация сигналов
