from django.contrib import admin
from .models import EmailConfirmation, SMSConfirmation


@admin.register(EmailConfirmation)
class ConfirmationAdmin(admin.ModelAdmin):
    list_display = ('email', 'signature', 'confirmed')
    readonly_fields = ('signature', 'confirmed')

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SMSConfirmation)
class SMSConfirmationAdmin(admin.ModelAdmin):
    list_display = ('phone', 'signature', 'confirmed')

    def has_change_permission(self, request, obj=None):
        return False
