from django.urls import path
from .views import CodeSendView, CodeVerifyView


app_name = 'confirmation_service'

urlpatterns = [
    path('code/send/', CodeSendView.as_view(), name='send-code'),
    path('code/verify/', CodeVerifyView.as_view(), name='code-verify'),
]
