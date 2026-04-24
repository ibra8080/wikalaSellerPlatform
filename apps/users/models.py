from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        SELLER = 'seller', 'Seller'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.SELLER
    )

    def __str__(self):
        return self.email
