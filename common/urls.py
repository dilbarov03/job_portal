from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from .views import UserRegisterView, UserProfileView, RecoverPasswordView

urlpatterns = [
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path("register", UserRegisterView.as_view(), name="register"),
    path("profile", UserProfileView.as_view()),
    path("recover-password", RecoverPasswordView.as_view()),
]
