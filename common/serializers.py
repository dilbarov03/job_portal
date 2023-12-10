from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from common.utils import is_password_valid
from confirmation_service.models import EmailConfirmation
from .models import User


class RegisterUserSerializer(serializers.ModelSerializer):
    """Serializer for creating user objects."""

    tokens = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'password', 'email', 'tokens')
        extra_kwargs = {'password': {'write_only': True}}

    def get_tokens(self, user):
        tokens = RefreshToken.for_user(user)
        refresh = str(tokens)
        access = str(tokens.access_token)
        data = {
            "refresh": refresh,
            "access": access
        }
        return data
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 6 characters")
        return value

    def create(self, validated_data):
        user = User(
            full_name=validated_data['full_name'],
            email=validated_data['email'],
            username=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()    
        return user
    

class RecoverPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    email = serializers.CharField(required=False, allow_null=True)
    signature = serializers.CharField(required=True)

    def validate(self, attrs):
        password = attrs.get('password', None)
        email = attrs.get('email', None)
        signature = attrs.get('signature', None)

        if is_password_valid(password)[0]:
            login = email

            User = get_user_model()
            user = User.objects.filter(username=login).first()
            if user:
                confirm_signature = EmailConfirmation.objects.filter(signature=signature).first()
                if confirm_signature is None:
                    raise serializers.ValidationError("Wrong signature")
                if confirm_signature.confirmed is False:
                    raise serializers.ValidationError(f"{login} is not confirmed!")


                user.set_password(password)
                user.save(commit=False)
                confirm_signature.delete()

                attrs['user'] = user
                return attrs

            else:
                raise serializers.ValidationError({'error': f"Bu {email} bilan foydalanuvchi mavjud emas"})

        else:
            raise serializers.ValidationError({'error': is_password_valid(password)[1]})    
