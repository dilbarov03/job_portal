from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SmsServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'confirmation_service'

    verbose_name = _("Сервис подтверждения")
