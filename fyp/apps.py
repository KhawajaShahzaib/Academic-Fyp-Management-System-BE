from django.apps import AppConfig

class FypConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fyp'
    # def ready(self):
    #     import fyp.signals  # Import the signals to activate them
