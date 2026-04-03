from django.db import models
from django.core.validators import MinValueValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.conf import settings  # За да вземем CustomUser модела
from inventory.models import Material, Category
from .services import ProductionService


class QuoteRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Очаква обработка (Нова)'),
        ('scheduled', 'Насрочен оглед'),
        ('measured', 'Взети размери (Чака оферта)'),
        ('ordered', 'Превърната в поръчка'),
        ('rejected', 'Отказана'),
    ]

    # Свързваме заявката с реалния потребител, който я е пуснал
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quote_requests',
        verbose_name="Клиент"
    )

    description = models.TextField(
        verbose_name="Описание на желанията",
        help_text="Опишете накратко какво желаете (напр. 2 прозореца за спалня, 1 балконска врата)"
    )
    address = models.CharField(max_length=255, verbose_name="Адрес за оглед/монтаж")
    phone_number = models.CharField(max_length=20, verbose_name="Телефон за връзка")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )

    notes = models.TextField(
        verbose_name="Бележки от фирмата",
        blank=True,
        null=True,
        help_text="Вътрешни бележки или отговор към клиента"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата на заявката")

    def __str__(self):
        return f"Заявка #{self.id} от {self.customer.username} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Заявка за оферта"
        verbose_name_plural = "Заявки за оферти"
        ordering = ['-created_at']


# --- След това обнови началото на твоя съществуващ модел Order ---
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Чакаща производство'),
        ('in_production', 'В производство'),
        ('ready', 'Готова за монтаж'),
        ('completed', 'Завършена'),
        ('cancelled', 'Отказана'),
    ]

    # ДОБАВЯМЕ: Връзка към заявката (ако поръчката произлиза от заявка)
    quote_request = models.OneToOneField(
        QuoteRequest,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='order',
        verbose_name="Базирана на заявка"
    )

    # Заменяме обикновеното текстово поле с реална връзка към потребителя(клиента)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name="Потребител(Клиент)",
        null=True
    )

    # Оставяме тези в случай че се поръчва на място и са нужни
    customer_name = models.CharField(max_length=100, verbose_name="Име на клиент (ако не е рег.)", blank=True,
                                     null=True)
    customer_phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True, null=True)
    delivery_address = models.CharField(max_length=255, verbose_name="Адрес за монтаж", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата на създаване")

    def __str__(self):
        name = self.customer.username if self.customer else self.customer_name
        return f"Поръчка #{self.id} - {name}"

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
        'inventory.Category',
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

    OPENING_MECHANISMS = [
        ('fixed', 'Фиксиран (без отваряне)'),
        ('turn', 'Въртящ (стандартно)'),
        ('tilt_turn', 'Въртящ и наклоняем'),
        ('sliding', 'Плъзгащ'),
        ('lift_sliding', 'Повдигащ-плъзгащ'),
    ]

    OPENING_DIRECTIONS = [
        ('left', 'Ляво'),
        ('right', 'Дясно'),
        ('up', 'Нагоре'),
        ('none', 'Без посока (фиксирано)'),
    ]

    opening_mechanism = models.CharField(
        max_length=20,
        choices=OPENING_MECHANISMS,
        default='turn',
        verbose_name="Механизъм на отваряне",
        help_text="Как се отваря прозорецът/вратата"
    )

    opening_direction = models.CharField(
        max_length=10,
        choices=OPENING_DIRECTIONS,
        default='left',
        verbose_name="Посока на отваряне",
        help_text="За врати: Ляво/Дясно | За прозорци: Ляво/Дясно (настрани) или Нагоре"
    )

    has_mullions = models.BooleanField(
        default=False,
        verbose_name="С делители",
        help_text="Има ли делители (импости) в прозореца"
    )

    mullion_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Брой делители",
        help_text="Брой вертикални делители (за 2 части = 1 делител, за 3 части = 2 делителя)"
    )

    is_equal_parts = models.BooleanField(
        default=True,
        verbose_name="Равни части",
        help_text="Дали частите са равни или неравни по ширина"
    )
    parts_count = models.PositiveIntegerField(
        default=1,
        verbose_name="Брой части",
        help_text="На колко части е разделен прозорецът (1, 2, 3...)"
    )

    parts_config = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Конфигурация на частите",
        help_text="Информация за всяка част - отваряема или фикс"
    )

    custom_widths = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Ръчни ширини",
        help_text="Ширини за неравни части"
    )

    materials = models.ManyToManyField(
        Material,
        blank=True,
        related_name='custom_products',
        verbose_name="Вложени материали/Обков"
    )

    total_sashes = models.PositiveIntegerField(
        default=1,
        verbose_name="Общ брой крила",
        help_text="Колко крила има прозорецът (обикновено 1, 2 или 3)"
    )

    openable_sashes = models.PositiveIntegerField(
        default=0,
        verbose_name="Отваряеми крила",
        help_text="Колко от крилата са отваряеми"
    )

    @property
    def glass_dimensions_data(self):
        """Връща пълни данни за размерите на стъклопакета"""
        return ProductionService.calculate_glass_dimensions(self)


    @property
    def glass_area(self):
        """Връща общата площ на стъклото за всички крила"""
        data = self.glass_dimensions_data
        return data['total_glass_area']


    @property
    def glass_details_list(self):
        """Връща списък с детайли за всяко крило"""
        data = self.glass_dimensions_data
        return data['details']

    @property
    def glass_size_per_sash(self):
        """Връща размера на стъклопакета като текст"""
        data = self.glass_dimensions_data
        return data['glass_dimensions']

    @property
    def sash_width(self):
        """Връща ширината на едно крило"""
        data = self.glass_dimensions_data
        return data['sash_width']

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