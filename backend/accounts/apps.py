from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        """
        Register signals for the accounts app.
        This ensures that profiles (AgentProfile, SupervisorProfile, etc.)
        are automatically created when a new User is registered.
        """
        import accounts.signals
