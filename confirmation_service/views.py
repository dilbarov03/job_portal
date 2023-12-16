from .serializers import EmailConfirmationSerializer, SMSConfirmationSerializer
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from drf_yasg import openapi

User = get_user_model()


class CodeSendView(APIView):
    state_param = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
        }
    )

    @swagger_auto_schema(request_body=state_param)
    def post(self, request):
        try:
            serializer = EmailConfirmationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except KeyError:
            return Response(
                {'error': "Invalid type", "types": self.action_serializer.keys()}, status=status.HTTP_404_NOT_FOUND)


class CodeVerifyView(APIView):
    state_param = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'signature': openapi.Schema(type=openapi.TYPE_STRING, description='Signature'),
            'code': openapi.Schema(type=openapi.TYPE_STRING, description='Code'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
        }
    )

    @swagger_auto_schema(request_body=state_param)
    def post(self, request):
        signature = request.data.get('signature', None)
        code = request.data.get('code', None)
        try:
            instance = EmailConfirmationSerializer.Meta.model.objects.get(signature=signature)
            serializer = EmailConfirmationSerializer(instance=instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.check_code(code)
            serializer.verify()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except KeyError:
            return Response(
                {'error': "Invalid type", "types": self.action_serializer.keys()}, status=status.HTTP_404_NOT_FOUND)
        except EmailConfirmationSerializer.Meta.model.DoesNotExist:
            return Response({"error": "Signature not found"}, status=status.HTTP_404_NOT_FOUND)
