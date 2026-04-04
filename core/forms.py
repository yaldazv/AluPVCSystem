from django import forms
from .models import ContactMessage

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Вашето име'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Вашият имейл адреc'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Тема на съобщението'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Как можем да ви помогнем?'}),
        }
