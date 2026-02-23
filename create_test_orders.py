"""
Скрипт за създаване на тестова поръчка готова за монтаж
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AluPVCSystem.settings')
django.setup()

from production.models import Order
from inventory.models import Category

# Създ��ване на тестова поръчка
order, created = Order.objects.get_or_create(
    customer_name='Тестов Клиент',
    defaults={
        'customer_phone': '0888123456',
        'delivery_address': 'ул. "Витоша" №15, гр. София',
        'status': 'ready',  # Готова за монтаж
    }
)

if created:
    print(f"✅ Създадена тестова поръчка: {order}")
else:
    # Ако вече съществува, актуализираме статуса
    order.status = 'ready'
    order.save()
    print(f"✅ Актуализирана поръчка: {order} - статус: готова за монтаж")

# Създаване на втора поръчка
order2, created2 = Order.objects.get_or_create(
    customer_name='Иван Иванов',
    defaults={
        'customer_phone': '0878987654',
        'delivery_address': 'бул. "България" №120, ап. 5, гр. Пловдив',
        'status': 'ready',
    }
)

if created2:
    print(f"✅ Създадена втора тестова поръчка: {order2}")
else:
    order2.status = 'ready'
    order2.save()
    print(f"✅ Актуализирана поръчка: {order2} - статус: готова за монтаж")

print("\n🎉 Готово! Сега можеш да тестваш създаването на монтажи.")
print(f"   Налични поръчки за монтаж: {Order.objects.filter(status='ready').count()}")

