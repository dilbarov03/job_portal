from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .utils import generate_confirmation_code, send_sms, send_email


class BaseConfirmation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip = models.CharField(null=True, blank=True, max_length=255)

    code = models.CharField(max_length=255)
    attempts = models.PositiveSmallIntegerField(default=0)
    code_expired_at = models.DateTimeField()
    confirmed = models.BooleanField(default=False)

    signature = models.CharField(max_length=32)
    lifetime_end = models.DateTimeField()

    class Meta:
        abstract = True

    def send_code(self, message_body: str) -> bool:
        """
        message = "Your code: %(code)s"
        example:
            message % {'code': 125432} => Your code: 125432
        """
        raise NotImplemented

    def check_code(self, code):
        """check is code correct"""
        if self.code_expired_at < timezone.now():
            success = False
            message = _("Срок действия кода истек.")
        elif self.code != code:
            success = False
            message = _("Неправильный код.")
        else:
            success = True
            message = _("Ok")
        return success, message

    @staticmethod
    def get_random_code() -> str:
        return generate_confirmation_code()


class SMSConfirmation(BaseConfirmation):
    phone = models.CharField(max_length=25)

    def send_code(self, message_body: str = None) -> bool:
        message_body = str(message_body or "Код подтверждения: %(code)s \nНикому не давайте код!")
        self.code = self.get_random_code()
        self.code_expired_at = timezone.now() + timedelta(seconds=settings.SMS_CONFIRMATION_CODE_EXPIRE_SECONDS)
        message = message_body % {'code': self.code}
        send_sms(self.phone, message)
        self.save()
        return True

    @classmethod
    def verify_signature(cls, signature, phone):
        return cls.objects.filter(signature=signature, phone=phone, confirmed=True).exists()

    class Meta:
        verbose_name = _("SMS confirmation")
        verbose_name_plural = _("SMS confirmations")


class EmailConfirmation(BaseConfirmation):
    email = models.EmailField(max_length=1024)

    def send_code(self, message_body: str = None) -> bool:
        message_body = str(message_body or "Код подтверждения: %(code)s \nНикому не давайте код!")
        self.code = self.get_random_code()
        self.code_expired_at = timezone.now() + timedelta(seconds=settings.SMS_CONFIRMATION_CODE_EXPIRE_SECONDS)
        message = message_body % {'code': self.code}
        send_email(self.email, 'Confirmation code', message)
        self.save()
        return True

    @staticmethod
    def verify_signature(cls, signature, email):
        return cls.objects.filter(signature=signature, email=email, confirmed=True).exists()

    class Meta:
        verbose_name = _("Email confirmation")
        verbose_name_plural = _("Email confirmations")
