from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name="Име на категория",
        unique=True
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Специфични настройки или бележки за категорията"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']


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
    'Category',
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
      null=True,
      blank=True,
      verbose_name="Дължина на прът (мм)",
      help_text="Стандартна дължина на един прът"
  )
  profile_width = models.PositiveIntegerField(
      null=True,
      blank=True,
      verbose_name="Ширина на профил (мм)",
      help_text="Монтажна ширина на профила (напр. 70мм, 82мм)"
  )

  falz_depth = models.PositiveIntegerField(
      null=True,
      blank=True,
      verbose_name="Дълбочина на фалца (мм)",
      help_text="Разстоянието от външния ръб до дъното където ляга стъклото (обикновено 18-20мм). Измерваш с ролетка."
  )

  wing_visible_width = models.PositiveIntegerField(
      null=True,
      blank=True,
      verbose_name="Видима част на крило (мм)",
      help_text="Ширина на профила минус дълбочина на фалца (напр. 80мм - 20мм = 60мм). Можеш да измериш директно или да въведеш от каталога."
  )

  mullion_width = models.PositiveIntegerField(
      null=True,
      blank=True,
      verbose_name="Ширина на делител (мм)",
      help_text="Пълна ширина на делител/импост (обикновено 60мм)"
  )

  overlap = models.PositiveIntegerField(
      null=True,
      blank=True,
      verbose_name="Застъпване (мм)",
      help_text="Колко се добавя към светлия отвор (обикновено 28-30мм, общо 14+14мм от всяка страна)"
  )

  material_type = models.CharField(
      max_length=50,
      choices=MATERIAL_TYPES,
      verbose_name="Тип на материала"
  )
  quantity_in_stock = models.FloatField(
      default=0,
      validators=[MinValueValidator(0.0, message="Наличността не може да бъде под нула!")],
      verbose_name="Налично количество"
  )
  unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        verbose_name="Мерна единица"
  )

  def save(self, *args, **kwargs):
      if not self.name or self.name.strip() == '':
          parts = []

          if self.brand:
              parts.append(self.brand)

          if self.profile_width:
              parts.append(f"{self.profile_width}мм")

          if self.profile_type:
              parts.append(self.get_profile_type_display())


          if self.color:
              parts.append(self.color)

          if not parts:
              parts.append(self.get_material_type_display())

          self.name = " ".join(parts)

      super().save(*args, **kwargs)

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


class Supplier(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Име на доставчик",
        unique=True
    )

    contact_person = models.CharField(
        max_length=100,
        verbose_name="Лице за контакт",
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        blank=True
    )

    email = models.EmailField(
        verbose_name="Email",
        blank=True
    )

    address = models.TextField(
        verbose_name="Адрес",
        blank=True
    )

    notes = models.TextField(
        verbose_name="Бележки",
        blank=True,
        help_text="Допълнителна информация за доставчика"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Деактивирайте доставчици, с които вече не работите"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Доставчик"
        verbose_name_plural = "Доставчици"
        ordering = ['name']


class Delivery(models.Model):
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        verbose_name="Материал",
        related_name="deliveries"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        verbose_name="Доставчик",
        related_name="deliveries"
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Количество",
        help_text="Доставено количество"
    )

    delivery_date = models.DateField(
        verbose_name="Дата на доставка",
        help_text="Кога пристигна доставката"
    )

    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена за единица",
        help_text="Цена на единица за тази доставка"
    )

    invoice_number = models.CharField(
        max_length=50,
        verbose_name="Номер на фактура",
        blank=True
    )

    notes = models.TextField(
        verbose_name="Бележки",
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Създадено на"
    )

    def __str__(self):
        return f"{self.material.name} - {self.quantity} {self.material.unit} ({self.delivery_date})"

    @property
    def total_price(self):
        return self.quantity * self.price_per_unit

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Проверка дали е нова доставка

        if is_new:
            self.material.quantity_in_stock += float(self.quantity)
            self.material.save()
        else:
            old_delivery = Delivery.objects.get(pk=self.pk)
            difference = self.quantity - old_delivery.quantity
            self.material.quantity_in_stock += float(difference)
            self.material.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.material.quantity_in_stock -= float(self.quantity)
        self.material.save()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Доставка"
        verbose_name_plural = "Доставки"
        ordering = ['-delivery_date', '-created_at']

