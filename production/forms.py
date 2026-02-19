from django import forms
from django.core.exceptions import ValidationError
from .models import Order, CustomProduct, ReadyProduct, Category
from inventory.models import Material
import re


class OrderForm(forms.ModelForm):
    """
    Форма за създаване и редакция на поръчки.
    Включва validation за телефон и адрес.
    """

    class Meta:
        model = Order
        fields = [
            'customer_name',
            'customer_phone',
            'delivery_address',
            'status',
        ]

        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Име на клиента',
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+359 88 123 4567 или 0888123456',
            }),
            'delivery_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ул. "Примерна" №10, гр. София',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

        labels = {
            'customer_name': 'Име на клиент',
            'customer_phone': 'Телефон за контакт',
            'delivery_address': 'Адрес за монтаж',
            'status': 'Статус на поръчката',
        }

        help_texts = {
            'customer_phone': 'Въведете валиден телефонен номер',
            'delivery_address': 'Пълен адрес където ще се извърши монтажа',
        }

    def clean_customer_name(self):
        """Валидация за име на клиент - минимум 2 символа, само букви и интервали"""
        name = self.cleaned_data.get('customer_name')
        if len(name) < 2:
            raise ValidationError('Името трябва да съдържа поне 2 символа!')
        if not all(char.isalpha() or char.isspace() for char in name):
            raise ValidationError('Името трябва да съдържа само букви!')
        return name.strip()

    def clean_customer_phone(self):
        """Валидация за телефонен номер - Bulgarian format"""
        phone = self.cleaned_data.get('customer_phone')
        # Премахва всички интервали и тирета
        phone_cleaned = phone.replace(' ', '').replace('-', '')

        # Проверка за Bulgarian phone patterns
        patterns = [
            r'^0[0-9]{9}$',  # 0888123456
            r'^\+3590[0-9]{9}$',  # +3590888123456
            r'^3590[0-9]{9}$',  # 3590888123456
        ]

        if not any(re.match(pattern, phone_cleaned) for pattern in patterns):
            raise ValidationError(
                'Моля въведете валиден телефонен номер! '
                'Примери: 0888123456, +359888123456'
            )

        return phone_cleaned

    def clean_delivery_address(self):
        """Валидация за адрес - минимум 10 символа"""
        address = self.cleaned_data.get('delivery_address')
        if len(address) < 10:
            raise ValidationError('Адресът е твърде кратък! Въведете пълен адрес.')
        return address.strip()


class OrderUpdateForm(OrderForm):
    """
    Форма за редакция на съществуваща поръчка.
    Прави някои полета read-only.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ако поръчката е завършена, не може да се променя клиента
        if self.instance and self.instance.status in ['completed', 'cancelled']:
            self.fields['customer_name'].widget.attrs['readonly'] = True
            self.fields['customer_phone'].widget.attrs['readonly'] = True
            self.fields['customer_name'].widget.attrs['class'] += ' bg-light'
            self.fields['customer_phone'].widget.attrs['class'] += ' bg-light'
            self.fields['customer_name'].help_text = 'Не може да се променя за завършени поръчки'


class CustomProductForm(forms.ModelForm):
    """
    Форма за добавяне на прозорци/врати към поръчка.
    Включва validation за размери и филтриране на материали по категория.
    """

    class Meta:
        model = CustomProduct
        fields = [
            'order',
            'category',
            'product_type',
            'width',
            'height',
            'sash_count',
            'opening_type',
            'materials',
        ]

        widgets = {
            'order': forms.Select(attrs={
                'class': 'form-select',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'product_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'width': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'мм',
                'min': '200',
                'step': '1',
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'мм',
                'min': '200',
                'step': '1',
            }),
            'sash_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10',
            }),
            'opening_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'materials': forms.CheckboxSelectMultiple(),
        }

        labels = {
            'order': 'Поръчка',
            'category': 'Категория (PVC/Алуминий)',
            'product_type': 'Тип продукт',
            'width': 'Ширина (мм)',
            'height': 'Височина (мм)',
            'sash_count': 'Брой крила',
            'opening_type': 'Тип отваряне',
            'materials': 'Допълнителни материали/обков',
        }

        help_texts = {
            'width': 'Минимална ширина: 200мм',
            'height': 'Минимална височина: 200мм',
            'sash_count': 'Колко крила има прозорецът/вратата',
            'materials': 'Изберете обков, дръжки и други материали',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Филтрира материалите - показва само релевантните за избраната категория
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['materials'].queryset = Material.objects.filter(
                    categories__id=category_id
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category:
            self.fields['materials'].queryset = Material.objects.filter(
                categories=self.instance.category
            )

    def clean_width(self):
        """Валидация за ширина - минимум 200мм, максимум 3000мм"""
        width = self.cleaned_data.get('width')
        if width < 200:
            raise ValidationError('Ширината не може да е по-малка от 200мм!')
        if width > 3000:
            raise ValidationError('Ширината не може да е по-голяма от 3000мм!')
        return width

    def clean_height(self):
        """Валидация за височина - минимум 200мм, максимум 3000мм"""
        height = self.cleaned_data.get('height')
        if height < 200:
            raise ValidationError('Височината не може да е по-малка от 200мм!')
        if height > 3000:
            raise ValidationError('Височината не може да е по-голяма от 3000мм!')
        return height

    def clean(self):
        """Cross-field validation за размери и тип"""
        cleaned_data = super().clean()
        width = cleaned_data.get('width')
        height = cleaned_data.get('height')
        product_type = cleaned_data.get('product_type')
        sash_count = cleaned_data.get('sash_count')

        # За врати, височината трябва да е по-голяма от ширината
        if product_type == 'door' and width and height:
            if width > height:
                self.add_error('height', 'За врати височината трябва да е по-голяма от ширината!')

        # Ако има повече от 1 крило, ширината трябва да е поне 600мм
        if sash_count and sash_count > 1 and width:
            if width < 600:
                self.add_error('width', f'За {sash_count} крила ширината трябва да е минимум 600мм!')

        return cleaned_data


class ReadyProductForm(forms.ModelForm):
    """
    Форма за добавяне на готови продукти (щори, гаражни врати).
    """

    class Meta:
        model = ReadyProduct
        fields = [
            'order',
            'name',
            'quantity',
            'unit_price',
        ]

        widgets = {
            'order': forms.Select(attrs={
                'class': 'form-select',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Щора externa 200x200, Гаражна врата 240x210',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
            }),
        }

        labels = {
            'order': 'Поръчка',
            'name': 'Наименование на продукта',
            'quantity': 'Количество',
            'unit_price': 'Цена за единица',
        }

        help_texts = {
            'name': 'Въведете точното наименование и размери',
            'unit_price': 'Цена за 1 брой',
        }

    def clean_name(self):
        """Валидация за име - минимум 5 символа"""
        name = self.cleaned_data.get('name')
        if len(name) < 5:
            raise ValidationError('Наименованието трябва да е поне 5 символа!')
        return name.strip()

    def clean_quantity(self):
        """Валидация за количество - минимум 1"""
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise ValidationError('Количеството трябва да е поне 1!')
        return quantity

    def clean_unit_price(self):
        """Валидация за цена - трябва да е положително число"""
        price = self.cleaned_data.get('unit_price')
        if price <= 0:
            raise ValidationError('Цената трябва да е по-голяма от нула!')
        return price
