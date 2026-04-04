from django.test import TestCase
from .models import CustomUser

class CustomUserModelTests(TestCase):
    def setUp(self):
        # Създаваме тестов потребител преди всеки тест
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com',
            role='Customer'
        )

    def test_1_user_creation(self):
        """Тества дали потребителят се създава правилно"""
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(self.user.username, 'testuser')

    def test_2_user_role_assignment(self):
        """Тества дали ролята по подразбиране/зададената роля се записва"""
        self.assertEqual(self.user.role, 'Customer')

    def test_3_user_string_representation(self):
        """Тества дали __str__ методът връща очаквания формат"""
        expected_string = f"{self.user.username} ({self.user.role})"
        self.assertEqual(str(self.user), expected_string)

    def test_4_admin_role_sets_staff_status(self):
        """Тества дали 'Admin' ролята автоматично прави потребителя is_staff и is_superuser"""
        admin_user = CustomUser.objects.create_user(
            username='adminuser',
            password='password123',
            role='Admin'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_5_staff_role_sets_staff_status_only(self):
        """Тества дали 'Staff' ролята прави потребителя is_staff, но НЕ и is_superuser"""
        staff_user = CustomUser.objects.create_user(
            username='staffuser',
            password='password123',
            role='Staff'
        )
        self.assertTrue(staff_user.is_staff)
        self.assertFalse(staff_user.is_superuser)
