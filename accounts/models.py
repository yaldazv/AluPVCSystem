from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # Добавяме Custom полета според изискването
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефонен номер")
    
    # Може да добавим и други полета, ако е нужно
    
    class Meta(AbstractUser.Meta):
        verbose_name = 'Потребител'
        verbose_name_plural = 'Потребители'
