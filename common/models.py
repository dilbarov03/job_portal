

# from django.conf import settings
from django.contrib.auth.models import AbstractUser

from django.db import models
# from django.utils import timezone


class User(AbstractUser):
    full_name = models.CharField(max_length=256)
    email = models.EmailField(
        ("email"),
        unique=True,
        error_messages={
            "error": ("Bunday email mavjud."),
        },
        null=True
    )
    avatar = models.ImageField(upload_to="images/", blank=True, null=True)
    slug = models.CharField(max_length=256, null=True, blank=True)
    
    created_at = models.DateTimeField(("date created"), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(("date updated"), auto_now=True)
    
    is_worker = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)

    # SETTINGS
    USERNAME_FIELD = "email"
    first_name = None
    last_name = None
    REQUIRED_FIELDS = ["username", "full_name"]

    def __str__(self):
        return f"{self.email}"

    class Meta:
        db_table = "user"
        swappable = "AUTH_USER_MODEL"
        verbose_name = ("user")
        verbose_name_plural = ("users")


class FAQ(models.Model):
    question = models.CharField(max_length=256)
    answer = models.TextField()

    def __str__(self):
        return f"{self.question}"

    class Meta:
        db_table = "faq"
        verbose_name = ("faq")
        verbose_name_plural = ("faqs")


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f"{self.user}"

    class Meta:
        db_table = "feedback"
        verbose_name = ("feedback")
        verbose_name_plural = ("feedbacks")
