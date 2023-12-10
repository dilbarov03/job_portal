from .serializers import EmailConfirmationSerializer, SMSConfirmationSerializer
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from drf_yasg import openapi

User = get_user_model()


class CodeSendView(APIView):
    action_serializer = {
        'phone': SMSConfirmationSerializer,
        'email': EmailConfirmationSerializer
    }
    state_param = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'type': openapi.Schema(type=openapi.TYPE_STRING, description='Type'),
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Phone'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
        }
    )

    @swagger_auto_schema(request_body=state_param)
    def post(self, request):
        _type = request.data.get('type', None)
        try:
            serializer = self.action_serializer[_type](data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except KeyError:
            return Response(
                {'error': "Invalid type", "types": self.action_serializer.keys()}, status=status.HTTP_404_NOT_FOUND)


class CodeVerifyView(APIView):
    action_serializer = {
        'phone': SMSConfirmationSerializer,
        'email': EmailConfirmationSerializer
    }
    state_param = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'type': openapi.Schema(type=openapi.TYPE_STRING, description='Type'),
            'signature': openapi.Schema(type=openapi.TYPE_STRING, description='Signature'),
            'code': openapi.Schema(type=openapi.TYPE_STRING, description='Code'),
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Phone'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
        }
    )

    @swagger_auto_schema(request_body=state_param)
    def post(self, request):
        _type = request.data.get('type', None)
        signature = request.data.get('signature', None)
        code = request.data.get('code', None)
        try:
            instance = self.action_serializer[_type].Meta.model.objects.get(signature=signature)
            serializer = self.action_serializer[_type](instance=instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.check_code(code)
            serializer.verify()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except KeyError:
            return Response(
                {'error': "Invalid type", "types": self.action_serializer.keys()}, status=status.HTTP_404_NOT_FOUND)
        except self.action_serializer[_type].Meta.model.DoesNotExist:
            return Response({"error": "Signature not found"}, status=status.HTTP_404_NOT_FOUND)
