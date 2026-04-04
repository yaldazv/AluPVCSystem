from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Order, QuoteRequest

User = get_user_model()

class ProductionTests(TestCase):
    def setUp(self):
        # Създаване на потребител и клиент за тестовете
        self.client = Client()
        self.customer_user = User.objects.create_user(
            username='testcustomer',
            password='password123',
            role='Customer'
        )
        self.staff_user = User.objects.create_user(
            username='teststaff',
            password='password123',
            role='Staff'
        )

        self.quote = QuoteRequest.objects.create(
            customer=self.customer_user,
            description='Test Quote',
            address='Test Address',
            phone_number='0888888888'
        )

        self.order = Order.objects.create(
            customer=self.customer_user,
            customer_name='Test Name',
            customer_phone='0888888888',
            delivery_address='Test Address',
            status='pending'
        )

    def test_11_quote_creation(self):
        """Тества създаването на Заявка за оглед"""
        self.assertEqual(QuoteRequest.objects.count(), 1)
        self.assertEqual(self.quote.status, 'pending')

    def test_12_order_creation(self):
        """Тества създаването на Поръчка"""
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(self.order.customer_name, 'Test Name')

    def test_13_order_list_view_access_unauthenticated(self):
        """Тества дали нелогнат потребител е пренасочен (LoginRequiredMixin)"""
        url = reverse('production:order-list')
        response = self.client.get(url)
        # Очакваме пренасочване (302) към страницата за вход
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_14_order_list_view_access_authenticated(self):
        """Тества дали логнат потребител има достъп до списъка с поръчки"""
        self.client.login(username='testcustomer', password='password123')
        url = reverse('production:order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'production/order_list.html')

    def test_15_quote_update_view_access_control(self):
        """Тества дали Клиент получава Forbidden (403) при опит да редактира статус на заявка"""
        self.client.login(username='testcustomer', password='password123')
        url = reverse('production:quote-update', args=[self.quote.id])
        response = self.client.get(url)
        # Според нашата логика в QuoteRequestUpdateView, потребителят трябва да е Admin или Staff
        self.assertEqual(response.status_code, 403)
