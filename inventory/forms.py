from django import forms
from django.core.exceptions import ValidationError
from .models import Material, Supplier, Delivery


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
            'profile_type',
            'chamber_count',
            'has_thermal_break',
            'bar_length',
            'profile_width',
            'unit',
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
            'profile_width': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '70',
                'min': '20',
                'max': '200',
            }),
            'unit': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

        labels = {
            'name': 'Име на материала',
            'color': 'Цвят',
            'material_type': 'Тип материал',
            'categories': 'Категории',
            'brand': 'Марка/Система',
            'profile_type': 'Вид профил',
            'chamber_count': 'Брой камери',
            'has_thermal_break': 'С термомост',
            'bar_length': 'Дължина на прът (мм)',
            'profile_width': 'Ширина на профил(мм)',
            'unit': 'Мерна единица',
        }

        help_texts = {
            'categories': 'За профили избери само ЕДНА (PVC или Алуминий). За аксесоари/обков може повече.',
            'chamber_count': 'Приложимо само за PVC профили',
            'has_thermal_break': 'Приложимо само за алуминиеви профили',
            'profile_width': 'Ширина на профила в мм (70, 82, 45 и т.н.)',
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Полето "Име" е незадължително - ще се генерира автоматично
        self.fields['name'].required = False
        self.fields['name'].widget.attrs['placeholder'] = 'Ще се генерира автоматично ако е празно'
        self.fields['name'].help_text = 'Оставете празно за автоматично генериране'

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if not name or name.strip() == '':
            return ''

        if len(name.strip()) < 3:
            raise ValidationError('Ако попълвате име ръчно, трябва да съдържа поне 3 символа!')

        return name.strip()


    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address', 'notes', 'is_active']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Име на фирмата'}),
            'contact_person': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Име на лицето за контакт'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+359...'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'name': 'Име на доставчик',
            'contact_person': 'Лице за контакт',
            'phone': 'Телефон',
            'email': 'Email',
            'address': 'Адрес',
            'notes': 'Бележки',
            'is_active': 'Активен',
        }


class DeliveryForm(forms.ModelForm):
    """Форма за регистриране на доставка"""

    class Meta:
        model = Delivery
        fields = ['material', 'supplier', 'quantity', 'delivery_date', 'price_per_unit', 'invoice_number', 'notes']

        widgets = {
            'material': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'price_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер на фактура'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

        labels = {
            'material': 'Материал',
            'supplier': 'Доставчик',
            'quantity': 'Количество',
            'delivery_date': 'Дата на доставка',
            'price_per_unit': 'Цена за единица',
            'invoice_number': 'Номер на фактура',
            'notes': 'Бележки',
        }

        help_texts = {
            'quantity': 'Количеството ще се добави автоматично към наличността',
            'price_per_unit': 'Цена за единица за тази доставка',
        }

    def clean_quantity(self):
        """Валидация за количество - трябва да е положително"""
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise ValidationError('Количеството трябва да е по-голямо от нула!')
        return quantity

    def clean_price_per_unit(self):
        """Валидация за цена - трябва да е положителна"""
        price = self.cleaned_data.get('price_per_unit')
        if price <= 0:
            raise ValidationError('Цената трябва да е по-голяма от нула!')
        return price
