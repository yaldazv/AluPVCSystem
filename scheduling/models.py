from django.db import models
from production.models import Order
from django.core.exceptions import ValidationError
from datetime import date


def validate_not_past(value):
    if value < date.today():
        raise ValidationError("Датата не може да е в миналото!")


class Installation(models.Model):
    # One-to-One: Всеки монтаж е точно за една поръчка
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name="Поръчка"
    )
    scheduled_date = models.DateField(
        validators=[validate_not_past],
        verbose_name="Планирана дата",
        help_text="Дата за монтаж"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Бележки"
    )

    def __str__(self):
        return f"Монтаж на {self.scheduled_date} за {self.order.customer_name}"

    class Meta:
        verbose_name = "Монтаж"
        verbose_name_plural = "Монтажи"
        ordering = ['scheduled_date']
