from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import User
from .serializers import RecoverPasswordSerializer, RegisterUserSerializer


class UserRegisterView(generics.CreateAPIView):
    """Handles creating and listing Users."""
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RecoverPasswordView(generics.CreateAPIView):
    serializer_class = RecoverPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            success = True
            return Response({"success": success})

