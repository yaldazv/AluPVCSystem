"""
Скрипт за добавяне на примерни материали в базата данни
Изпълнение: python manage.py shell < add_sample_materials.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AluPVCSystem.settings')
django.setup()

from inventory.models import Material, Category

# Проверка и създаване на категории
pvc_category, _ = Category.objects.get_or_create(
    name='PVC',
    defaults={'description': 'PVC профили и материали'}
)

aluminium_category, _ = Category.objects.get_or_create(
    name='Алуминий',
    defaults={'description': 'Алуминиеви профили'}
)

print("✅ Категории са създадени/намерени")

# ОБКОВ - най-важните за формата
materials_to_create = [
    {
        'name': 'Дръжка Hoppe Секурент бяло',
        'color': 'Бяло',
        'material_type': 'hardware',
        'brand': 'Hoppe',
        'unit': 'pcs',
    },
    {
        'name': 'Панти Roto NT 120kg',
        'color': 'Сребристо',
        'material_type': 'hardware',
        'brand': 'Roto',
        'unit': 'pcs',
    },
    {
        'name': 'Брава многоточкова Winkhaus',
        'color': 'Сребристо',
        'material_type': 'hardware',
        'brand': 'Winkhaus',
        'unit': 'pcs',
    },
    {
        'name': 'Уплътнител EPDM черен',
        'color': 'Черно',
        'material_type': 'accessory',
        'brand': 'Standard',
        'unit': 'm',
    },
    {
        'name': 'Силикон Soudal прозрачен',
        'color': 'Прозрачен',
        'material_type': 'accessory',
        'brand': 'Soudal',
        'unit': 'pcs',
    },
    {
        'name': 'Монтажна пяна Makroflex 750ml',
        'color': 'Жълто',
        'material_type': 'accessory',
        'brand': 'Makroflex',
        'unit': 'pcs',
    },
    # ПРОФИЛИ PVC
    {
        'name': 'Каса 70mm бяло',
        'color': 'Бяло',
        'material_type': 'profile',
        'brand': 'Aluplast',
        'profile_type': 'frame',
        'profile_width': 70,
        'wing_visible_width': 35,
        'falz_depth': 16,
        'chamber_count': 5,
        'bar_length': 6000,
        'unit': 'm',
    },
    {
        'name': 'Крило 70mm бяло',
        'color': 'Бяло',
        'material_type': 'profile',
        'brand': 'Aluplast',
        'profile_type': 'sash',
        'profile_width': 70,
        'wing_visible_width': 40,
        'falz_depth': 16,
        'chamber_count': 5,
        'bar_length': 6000,
        'unit': 'm',
    },
    {
        'name': 'Делител 60mm бяло',
        'color': 'Бяло',
        'material_type': 'profile',
        'brand': 'Aluplast',
        'profile_type': 'mullion',
        'profile_width': 60,
        'chamber_count': 3,
        'bar_length': 6000,
        'unit': 'm',
    },
]

created_count = 0
skipped_count = 0

for mat_data in materials_to_create:
    # Проверка дали материалът вече съществува
    exists = Material.objects.filter(name=mat_data['name']).exists()

    if not exists:
        material = Material.objects.create(**mat_data)

        # Добавяне на категории за профилите
        if mat_data['material_type'] == 'profile':
            if 'PVC' in mat_data['name'] or 'Aluplast' in mat_data['brand']:
                material.categories.add(pvc_category)

        created_count += 1
        print(f"✅ Създаден: {mat_data['name']}")
    else:
        skipped_count += 1
        print(f"⏭️  Пропуснат (вече съществува): {mat_data['name']}")

print(f"\n📊 Обобщение:")
print(f"   - Създадени: {created_count}")
print(f"   - Пропуснати: {skipped_count}")
print(f"   - Общо: {created_count + skipped_count}")
print("\n🎉 Готово! Сега можеш да използваш материалите във формата за прозорци.")

