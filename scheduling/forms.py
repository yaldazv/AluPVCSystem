from django import forms
from django.core.exceptions import ValidationError
from .models import Installation
from production.models import Order
from datetime import date, timedelta


class InstallationForm(forms.ModelForm):
    """
    Форма за планиране на монтажи.
    Включва validation за дата и проверка дали поръчката е готова за монтаж.
    """

    class Meta:
        model = Installation
        fields = [
            'order',
            'scheduled_date',
            'notes',
        ]

        widgets = {
            'order': forms.Select(attrs={
                'class': 'form-select',
            }),
            'scheduled_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat(),
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Допълнителни бележки за монтажа...',
            }),
        }

        labels = {
            'order': 'Поръчка',
            'scheduled_date': 'Планирана дата за монтаж',
            'notes': 'Бележки',
        }

        help_texts = {
            'scheduled_date': 'Изберете дата в бъдещето',
            'notes': 'Всякакви важни детайли за монтажа',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Филтрира само поръчки, които са готови за монтаж
        self.fields['order'].queryset = Order.objects.filter(
            status__in=['ready', 'in_production']
        ).order_by('-created_at')

        # Променя празното съобщение
        self.fields['order'].empty_label = '-- Изберете поръчка --'

    def clean_order(self):
        """Валидация за поръчка - трябва да е ready или in_production"""
        order = self.cleaned_data.get('order')

        if order.status == 'completed':
            raise ValidationError('Тази поръчка вече е завършена!')

        if order.status == 'cancelled':
            raise ValidationError('Тази поръчка е отказана!')

        if order.status == 'pending':
            raise ValidationError(
                'Тази поръчка все още е в очакване. '
                'Променете статуса й на "В производство" преди да планирате монтаж.'
            )

        return order

    def clean_scheduled_date(self):
        """Валидация за дата - не може да е в миналото и не може да е в събота/неделя"""
        scheduled_date = self.cleaned_data.get('scheduled_date')

        # Проверка за минало
        if scheduled_date < date.today():
            raise ValidationError('Датата не може да е в миналото!')

        # Проверка за прекалено близка дата (трябва поне 2 дни предварително)
        min_date = date.today() + timedelta(days=2)
        if scheduled_date < min_date:
            raise ValidationError(
                f'Моля планирайте монтажа поне 2 дни предварително! '
                f'Най-ранна дата: {min_date.strftime("%d.%m.%Y")}'
            )

        # Проверка за почивни дни (събота=5, неделя=6)
        if scheduled_date.weekday() in [5, 6]:
            raise ValidationError('Не можем да монтираме в събота или неделя!')

        return scheduled_date

    def clean(self):
        """Cross-field validation - проверка дали вече има монтаж за същата дата"""
        cleaned_data = super().clean()
        scheduled_date = cleaned_data.get('scheduled_date')
        order = cleaned_data.get('order')

        if scheduled_date:
            # Проверка за прекалено натоварен ден (максимум 3 монтажа на ден)
            installations_on_date = Installation.objects.filter(
                scheduled_date=scheduled_date
            )

            # Ако редактираме съществуващ монтаж, не го броим
            if self.instance.pk:
                installations_on_date = installations_on_date.exclude(pk=self.instance.pk)

            if installations_on_date.count() >= 3:
                self.add_error(
                    'scheduled_date',
                    f'На {scheduled_date.strftime("%d.%m.%Y")} вече има 3 планирани монтажа! '
                    f'Изберете друга дата.'
                )

        return cleaned_data


class InstallationUpdateForm(InstallationForm):
    """
    Форма за редакция на съществуващ монтаж.
    Прави полето 'order' read-only.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Поръчката не може да се променя след създаване
        self.fields['order'].widget.attrs['disabled'] = True
        self.fields['order'].widget.attrs['class'] += ' bg-light'
        self.fields['order'].help_text = 'Поръчката не може да се променя след създаване на монтажа'

    def clean_order(self):
        """При редакция, връща текущата поръчка (не може да се променя)"""
        # Disabled полетата не се изпращат в POST data, затова връщаме instance value
        return self.instance.order
