from django import forms
from django.core.exceptions import ValidationError
from .models import Material


class MaterialForm(forms.ModelForm):
    """
    Форма за добавяне и редакция на материали.
    Включва custom validation, read-only полета и красиви widgets.
    """

    class Meta:
        model = Material
        fields = [
            'name',
            'color',
            'material_type',
            'categories',
            'brand',
            'series',
            'profile_type',
            'chamber_count',
            'has_thermal_break',
            'bar_length',
            'quantity',
            'unit',
            'price_per_unit',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Въведете име на материала',
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Бяло, Златен дъб, RAL 7016',
            }),
            'material_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'categories': forms.CheckboxSelectMultiple(),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'REHAU, Aluplast, ETEM...',
            }),
            'series': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '70мм, 82мм, E-45...',
            }),
            'profile_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'chamber_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '3, 5, 6, 7...',
                'min': '1',
            }),
            'has_thermal_break': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'bar_length': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '6000',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.0',
                'step': '0.01',
            }),
            'unit': forms.Select(attrs={
                'class': 'form-select',
            }),
            'price_per_unit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
            }),
        }

        labels = {
            'name': 'Име на материала',
            'color': 'Цвят',
            'material_type': 'Тип материал',
            'categories': 'Категории (PVC/Алуминий)',
            'brand': 'Марка/Система',
            'series': 'Серия',
            'profile_type': 'Вид профил',
            'chamber_count': 'Брой камери',
            'has_thermal_break': 'С термомост',
            'bar_length': 'Дължина на прът (мм)',
            'quantity': 'Налично количество',
            'unit': 'Мерна единица',
            'price_per_unit': 'Цена за единица',
        }

        help_texts = {
            'categories': 'Изберете за кои категории се използва този материал',
            'chamber_count': 'Приложимо само за PVC профили',
            'has_thermal_break': 'Приложимо само за алуминиеви профили',
            'quantity': 'Колко единици има на склад в момента',
        }

    def clean_name(self):
        """Валидация за име - минимум 3 символа"""
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise ValidationError('Името трябва да съдържа поне 3 символа!')
        return name.strip()

    def clean_price_per_unit(self):
        """Валидация за цена - трябва да е положително число"""
        price = self.cleaned_data.get('price_per_unit')
        if price <= 0:
            raise ValidationError('Цената трябва да е по-голяма от нула!')
        return price

    def clean_quantity(self):
        """Валидация за количество - не може да е отрицателно"""
        quantity = self.cleaned_data.get('quantity')
        if quantity < 0:
            raise ValidationError('Количеството не може да бъде отрицателно!')
        return quantity

    def clean(self):
        """
        Cross-field validation:
        - Ако material_type е 'profile', полетата за профили стават задължителни
        - Ако е PVC, chamber_count е задължително
        - Ако е алуминий, has_thermal_break се показва
        """
        cleaned_data = super().clean()
        material_type = cleaned_data.get('material_type')
        profile_type = cleaned_data.get('profile_type')
        chamber_count = cleaned_data.get('chamber_count')
        categories = cleaned_data.get('categories')

        # Ако е профил, profile_type е задължително
        if material_type == 'profile' and not profile_type:
            self.add_error('profile_type', 'За профили трябва да изберете вид профил!')

        # Ако е PVC профил, chamber_count е задължително
        if material_type == 'profile' and categories:
            category_names = [cat.name.lower() for cat in categories]
            if 'pvc' in category_names and not chamber_count:
                self.add_error('chamber_count', 'За PVC профили трябва да въведете брой камери!')

        return cleaned_data


class MaterialUpdateForm(MaterialForm):
    """
    Форма за редакция на съществуващ материал.
    Прави полето 'quantity' read-only (не може да се променя директно).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Прави quantity read-only
        self.fields['quantity'].widget.attrs['readonly'] = True
        self.fields['quantity'].widget.attrs['class'] += ' bg-light'
        self.fields['quantity'].help_text = 'Количеството се променя автоматично при доставки и производство'
