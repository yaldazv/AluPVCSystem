from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


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

    def save(self, *args, **kwargs):
        if self.role == self.RoleChoices.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        # Махаме 'else' блока, който занулява всичко,
        # за да не чупим суперпотребителите създадени ръчно.
        super().save(*args, **kwargs)

@receiver(post_save, sender=CustomUser)
def assign_user_to_group(sender, instance, created, **kwargs):
    if instance.role:
        group, _ = Group.objects.get_or_create(name=instance.role)
        instance.groups.clear()
        instance.groups.add(group)
