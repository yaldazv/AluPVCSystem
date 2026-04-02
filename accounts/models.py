from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    class RoleChoices(models.TextChoices):
        ADMIN = 'Admin', 'Admin'
        STAFF = 'Staff', 'Staff'
        CUSTOMER = 'Customer', 'Customer'
        SUPPLIER = 'Supplier', 'Supplier'

    role = models.CharField(
        max_length=15,
        choices=RoleChoices.choices,
        default=RoleChoices.CUSTOMER
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True) # Полезно за доставчици и бизнес клиенти

    def __str__(self):
        return f"{self.username} ({self.role})"