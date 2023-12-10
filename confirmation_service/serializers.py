from rest_framework import serializers
from .models import EmailConfirmation, SMSConfirmation
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .utils import get_randon_string


class ConfirmationSerializerMixin:

    def validate_signature(self, value):
        if self.instance.signature != value:
            raise serializers.ValidationError(_("Неправильная подпись."))
        return value

    def verify(self):
        self.instance.confirmed = True
        self.instance.save()

    def check_code(self, code):
        if self.instance.confirmed:
            raise serializers.ValidationError({'code': [_("Код уже подтвержден.")]})
        self.instance.attempts += 1
        self.instance.save()
        success, message = self.instance.check_code(code)
        if not success:
            raise serializers.ValidationError({'code': [message]})

    def create(self, validated_data):
        validated_data.update({
            "code_expired_at": timezone.now() + timedelta(seconds=settings.CONFIRMATION_CODE_EXPIRE_SECONDS),
            "lifetime_end": timezone.now() + timedelta(seconds=settings.CONFIRMATION_CODE_EXPIRE_SECONDS),
            'signature': get_randon_string(),
        })
        instance = self.Meta.model.objects.create(**validated_data)
        instance.send_code()
        return instance


class SMSConfirmationSerializer(ConfirmationSerializerMixin, serializers.ModelSerializer):
    phone = serializers.CharField(required=True)

    class Meta:
        model = SMSConfirmation
        fields = ('phone', 'signature', 'confirmed')
        read_only_fields = ('signature', 'confirmed')


class EmailConfirmationSerializer(ConfirmationSerializerMixin, serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = EmailConfirmation
        fields = ('email', 'signature', 'confirmed')
        read_only_fields = ('signature', 'confirmed')
