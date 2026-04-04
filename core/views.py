from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactMessageForm

def home_view(request):
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вашето съобщение беше изпратено успешно! Ще се свържем с вас скоро.')
            return redirect('home')
        else:
            messages.error(request, 'Имаше грешка при изпращането на съобщението. Моля, проверете данните.')
    else:
        form = ContactMessageForm()

    return render(request, 'home.html', {'form': form})
