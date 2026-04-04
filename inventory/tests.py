from django.test import TestCase
from .models import Category, Material, Supplier


class InventoryModelsTests(TestCase):
    def setUp(self):
        # Създаване на тестови данни
        self.category = Category.objects.create(name='PVC Profiles', description='Тест описание')
        self.supplier = Supplier.objects.create(name='Test Supplier', phone='0888123456')

        self.material = Material.objects.create(
            name='Test Profile',
            color='White',
            material_type='profile',
            unit='m',
            quantity_in_stock=100.5
            # Премахнато е несъществуващото поле min_quantity_threshold!
        )
        self.material.categories.add(self.category)

    def test_6_category_creation(self):
        """Тества създаването на категория и нейния __str__ метод"""
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(str(self.category), 'PVC Profiles')
        self.assertEqual(self.category.description, 'Тест описание')

    def test_7_supplier_creation(self):
        """Тества създаването на доставчик и запазването на полетата"""
        self.assertEqual(Supplier.objects.count(), 1)
        self.assertEqual(self.supplier.phone, '0888123456')
        self.assertTrue(self.supplier.is_active)

    def test_8_material_creation(self):
        """Тества създаването на материал и правилното задаване на количества"""
        self.assertEqual(Material.objects.count(), 1)
        self.assertEqual(self.material.quantity_in_stock, 100.5)
        self.assertEqual(self.material.unit, 'm')

    def test_9_material_category_relationship(self):
        """Тества Many-to-Many връзката между Материал и Категория"""
        self.assertIn(self.category, self.material.categories.all())
        self.assertEqual(self.material.categories.count(), 1)

    def test_10_material_string_representation(self):
        """Тества дали __str__ методът при материалите връща очаквания 'Име - Цвят' формат"""
        expected_string = "Test Profile - White"
        self.assertEqual(str(self.material), expected_string)
