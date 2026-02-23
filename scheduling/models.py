from django.db import models
from production.models import Order
from django.core.exceptions import ValidationError
from datetime import date


def validate_not_past(value):
    if value < date.today():
        raise ValidationError("Датата не може да е в миналото!")


class Installation(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Планиран'),
        ('in_progress', 'В процес'),
        ('completed', 'Завършен'),
        ('cancelled', 'Отменен'),
    ]

    installation_date = models.DateField(
        validators=[validate_not_past],
        verbose_name="Дата на монтаж",
        help_text="Дата за монтаж"
    )

    orders = models.ManyToManyField(
        Order,
        verbose_name="Поръчки",
        related_name='installations',
        help_text="Поръчки, които ще се монтират на тази дата"
    )

    address = models.CharField(
        max_length=500,
        verbose_name="Адрес на монтаж",
        help_text="Пълен адрес където ще се извърши монтажът"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name="Статус"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Бележки",
        help_text="Допълнителни бележки за монтажа"
    )

    def __str__(self):
        order_count = self.orders.count()
        return f"Монтаж на {self.installation_date} ({order_count} поръчки)"

    class Meta:
        verbose_name = "Монтаж"
        verbose_name_plural = "Монтажи"
        ordering = ['installation_date']
