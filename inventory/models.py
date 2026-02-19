from django.core.validators import MinValueValidator
from django.db import models


class Material(models.Model):
  MATERIAL_TYPES = [
      ('profile', 'Профил'),
      ('glass', 'Стъклопакет'),
      ('accessory', 'Аксесоар'),
      ('hardware', 'Обков'),
      ('other', 'Други'),
  ]

  UNIT_CHOICES = [
      ('m', 'Линеен метър'),
      ('sqm', 'Kвадратен метър'),
      ('pcs', 'Брой'),
  ]

  name = models.CharField(
      max_length=100,
      verbose_name="Име на материала"
  )
  color = models.CharField(
      max_length=100,
      verbose_name="Цвят на материала"
  )
  categories = models.ManyToManyField(
      'production.Category',
      related_name='materials',
      verbose_name="Категории",
      blank=True,
      help_text="Изберете за кои категории е приложим материалът (PVC, Алуминий и т.н.)"
  )
  brand = models.CharField(
      max_length=100,
      blank=True,
      verbose_name="Марка/Система",
      help_text="Например: REHAU, Aluplast, ETEM, Profilink"
  )
  series = models.CharField(
      max_length=50,
      blank=True,
      verbose_name="Серия",
      help_text="Например: 70мм, 82мм, E-45"
  )

  chamber_count = models.PositiveIntegerField(
      null=True,
      blank=True,
      verbose_name="Брой камери",
      help_text="Само за PVC профили (3, 5, 6, 7 камери)"
  )

  has_thermal_break = models.BooleanField(
      default=False,
      verbose_name="С термомост",
      help_text="Приложимо само за алуминиеви профили"
  )

  PROFILE_TYPES = [
      ('frame', 'Каса'),
      ('sash', 'Крило'),
      ('mullion', 'Делител'),
      ('glazing_bead', 'Стъклодържател'),
      ('z_profile', 'Z-профил'),
      ('other', 'Друг'),
  ]

  profile_type = models.CharField(
      max_length=20,
      choices=PROFILE_TYPES,
      blank=True,
      verbose_name="Вид профил",
      help_text="Приложимо за материали от тип 'Профил'"
  )

  bar_length = models.PositiveIntegerField(
      default=6000,
      verbose_name="Дължина на прът (мм)",
      help_text="Стандартна дължина на един прът"
  )

  material_type = models.CharField(
      max_length=50,
      choices=MATERIAL_TYPES,
      verbose_name="Тип на материала"
  )
  quantity = models.FloatField(
      validators=[MinValueValidator(0.0, message="Наличността не може да бъде под нула!")],
      verbose_name="Количество"
  )
  unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        verbose_name="Мерна единица"
  )
  price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message="Цената не може да e <= 0!")],
        verbose_name="Цена за единица"
  )


  # ⬇️ ЗАМЕНИ ТОЗИ МЕТОД ⬇️
  def __str__(self):
      parts = [self.name]
      if self.brand:
          parts.append(f"[{self.brand}]")
      if self.color:
          parts.append(f"({self.color})")
      return " ".join(parts)

  class Meta:
      verbose_name = "Материал"
      verbose_name_plural = "Материали"
