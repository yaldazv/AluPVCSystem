import time
from django.core.mail import send_mail
from django.conf import settings


def send_order_ready_email(order_id, customer_email, customer_name):
    """
    Асинхронна задача, която симулира забавяне (напр. генериране на PDF)
    и изпраща имейл до клиента.
    """
    # 1. Симулираме тежка операция (напр. генериране на чертежи) - чакаме 5 секунди
    time.sleep(5)

    # 2. Изпращаме имейла
    subject = f"AluPVC System: Вашата поръчка #{order_id} е ГОТОВА!"
    message = f"Здравейте, {customer_name},\n\nРадваме се да ви съобщим, че вашата поръчка #{order_id} е изработена и е готова за монтаж!\nНаш екип ще се свърже с вас скоро за уговаряне на час.\n\nПоздрави,\nЕкипът на AluPVC System"

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[customer_email],
        fail_silently=False,
    )

    return f"Имейлът за поръчка #{order_id} беше успешно изпратен до {customer_email}."
