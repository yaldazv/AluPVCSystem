from django import forms
from django.core.exceptions import ValidationError
from .models import Installation
from production.models import Order
from datetime import date


class InstallationForm(forms.ModelForm):

    class Meta:
        model = Installation
        fields = [
            'installation_date',
            'orders',
            'address',
            'status',
            'notes',
        ]

        widgets = {
            'installation_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat(),
                'id': 'id_installation_date',
            }),
            'orders': forms.CheckboxSelectMultiple(attrs={
                'class': 'order-checkbox',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Адрес за монтаж...',
                'id': 'id_address',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Допълнителни бележки за монтажа...',
            }),
        }

        labels = {
            'installation_date': 'Дата на монтаж',
            'orders': 'Изберете поръчки за монтаж',
            'address': 'Адрес на монтаж',
            'status': 'Статус',
            'notes': 'Бележки',
        }

        help_texts = {
            'installation_date': 'Изберете дата за монтаж',
            'orders': 'Можете да изберете една или повече поръчки за този монтаж',
            'address': 'Адресът ще се попълни автоматично при избор на първата поръчка',
            'notes': 'Всякакви важни детайли за монтажа',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['orders'].queryset = Order.objects.filter(
            status__in=['ready', 'in_production']
        ).order_by('-created_at')

    def clean_orders(self):
        orders = self.cleaned_data.get('orders')

        if not orders or orders.count() == 0:
            raise ValidationError('Трябва да изберете поне една поръчка!')


        for order in orders:
            if order.status == 'completed':
                raise ValidationError(f'Поръчка "{order}" вече е завършена!')

            if order.status == 'cancelled':
                raise ValidationError(f'Поръчка "{order}" е отказана!')

            if order.status == 'pending':
                raise ValidationError(
                    f'Поръчка "{order}" все още е в очакване. '
                    'Променете статуса й на "В производство" преди да планирате монтаж.'
                )

        return orders

    def clean_installation_date(self):
        installation_date = self.cleaned_data.get('installation_date')

        if installation_date < date.today():
            raise ValidationError('Датата не може да е в миналото!')

        return installation_date

