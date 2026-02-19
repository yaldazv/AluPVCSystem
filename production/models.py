from django.db import models
from django.core.validators import MinValueValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from inventory.models import Material
from .services import ProductionService


class Category(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name="Име на категория",
        unique=True
    )

    system_offset = models.PositiveIntegerField(
        default=50,
        verbose_name="Технологичен офсет (мм)",
        help_text="Разстоянието, с което профилът застъпва стъклото (стандартно 50мм)"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Специфични настройки или бележки за категорията"
    )

    def __str__(self):
        # По-добре е да виждаш и офсета в името, когато избираш категория
        return f"{self.name} ({self.system_offset}мм офсет)"

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Чакаща'),
        ('in_production', 'В производство'),
        ('ready', 'Готова за монтаж'),
        ('completed', 'Завършена'),
        ('cancelled', 'Отказана'),
    ]

    customer_name = models.CharField(
        max_length=100,
        verbose_name="Клиент",
        validators=[MinLengthValidator(2)]
    )
    customer_phone = models.CharField(max_length=20, verbose_name="Телефон")
    delivery_address = models.CharField(max_length=255, verbose_name="Адрес за монтаж")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата на създаване")

    def __str__(self):
        return f"Поръчка #{self.id} - {self.customer_name}"

    class Meta:
        verbose_name = "Поръчка"
        verbose_name_plural = "Поръчки"
        ordering = ['-created_at']


class CustomProduct(models.Model):
    """Обединен модел за Прозорци и Врати"""
    PRODUCT_TYPES = [
        ('window', 'Прозорец'),
        ('door', 'Врата'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Поръчка"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name="Вид профил (Категория)"
    )
    product_type = models.CharField(
        max_length=10,
        choices=PRODUCT_TYPES,
        verbose_name="Тип продукт"
    )

    width = models.FloatField(
        validators=[MinValueValidator(200)],
        verbose_name="Ширина (мм)"
    )
    height = models.FloatField(
        validators=[MinValueValidator(200)],
        verbose_name="Височина (мм)"
    )
    sash_count = models.PositiveIntegerField(
        default=1,
        verbose_name="Брой крила",
        help_text="Колко крила има прозорецът/вратата (1, 2, 3...)"
    )

    OPENING_TYPES = [
        ('fixed', 'Фиксиран (без отваряне)'),
        ('turn', 'Едноврилен (въртящ)'),
        ('tilt_turn', 'Двукрилен (въртящ и наклоняем)'),
        ('sliding', 'Плъзгащ'),
        ('lift_sliding', 'Повдигащ-плъзгащ'),
    ]

    opening_type = models.CharField(
        max_length=20,
        choices=OPENING_TYPES,
        default='turn',
        verbose_name="Тип отваряне",
        help_text="Как се отваря прозорецът/вратата"
    )

    # Many-to-Many за консумативи (обков, дръжки, мрежи)
    materials = models.ManyToManyField(
        Material,
        blank=True,
        related_name='custom_products',
        verbose_name="Вложени материали/Обков"
    )

    @property
    def glass_area(self):
        """Връща площта на стъклото за рязане"""
        data = ProductionService.calculate_dimensions_and_areas(self)
        return data['glass_area']

    @property
    def total_materials_price(self):
        """Връща цената на вложените материали"""
        return ProductionService.calculate_material_only_price(self)

    def calculate_total_area(self):
        """Пресмята общата площ в кв.м."""
        return (self.width * self.height) / 1_000_000

    def get_material_costs(self):
        """
        Изчислява цената само на базата на вложените материали от склада.
        Формула: $$\sum (Material.Price \times Quantity)$$
        """
        # В реална ситуация тук ще импортираш ProductionService,
        # но за простота го дефинираме вътре:
        total = 0
        # 1. Сумираме цените на всички избрани материали (дръжки, панти и т.н.)
        for material in self.materials.all():
            total += float(material.price_per_unit)

        # 2. Можеш да добавиш логика за цена на кв.м. стъкло,
        # ако стъклото е записано като материал в склада
        return round(total, 2)

    def __str__(self):
        return f"{self.get_product_type_display()} - {self.width}x{self.height} ({self.category.name})"

    class Meta:
        verbose_name = "Прозорец/Врата"
        verbose_name_plural = "Прозорци и Врати"


class ReadyProduct(models.Model):
    """За готови продукти като щори и гаражни врати"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ready_products')
    name = models.CharField(max_length=100, verbose_name="Наименование")
    quantity = models.PositiveIntegerField(default=1)
    # Тук цената се взема директно за брой
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за брой")

    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.name} - {self.quantity} бр."

    class Meta:
        verbose_name = "Готов продукт"
        verbose_name_plural = "Готови продукти"