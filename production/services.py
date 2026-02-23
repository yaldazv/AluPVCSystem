from decimal import Decimal


class ProductionService:
    """Бизнес логика за изчисления свързани с производството"""

    @staticmethod
    def calculate_glass_dimensions(product):
        """
        Изчислява размерите на стъклопакетите за даден прозорец/врата.

        Връща dict с:
        - glass_dimensions: текст с описание на всички стъклопакети
        - total_glass_area: обща площ в кв.м
        - sash_width: ширина на едно крило в мм
        - details: списък с детайли за всяко крило
        """

        # Вземаме размерите на целия прозорец
        total_width = product.width
        total_height = product.height

        # Брой крила
        total_sashes = product.total_sashes
        openable_sashes = product.openable_sashes
        fixed_sashes = total_sashes - openable_sashes

        # Ширина на едно крило (ако има повече от 1, делим равно)
        sash_width = total_width / total_sashes if total_sashes > 0 else total_width

        # Намаляване за профила (зависи от материала)
        # Ще използваме категорията за да вземем профилната ширина
        category = product.category

        # Вземаме материалите свързани с продукта (ако има)
        # Търсим профил тип "Каса" или "Крило" за да вземем ширината
        frame_material = product.materials.filter(profile_type='frame').first()
        wing_material = product.materials.filter(profile_type='wing').first()

        # Ако няма зададени материали, използваме стандартни стойности
        if frame_material and hasattr(frame_material, 'profile_width'):
            frame_width = frame_material.profile_width or 70
        else:
            frame_width = 70  # стандартна ширина на касата в мм

        if wing_material and hasattr(wing_material, 'wing_visible_width'):
            wing_visible = wing_material.wing_visible_width or 50
        else:
            wing_visible = 50  # стандартна видима част на крилото

        # Константа за застъпване (технологичен луфт)
        overlap = 20  # мм

        # Списък за детайлите на всяко крило
        sash_details = []
        total_area = 0

        # Изчисляваме за всяко крило
        for i in range(1, total_sashes + 1):
            is_openable = i <= openable_sashes

            # Изчисляваме размера на стъклопакета за това крило
            if is_openable:
                # Отваряемо крило: намаляваме с каса + крило
                glass_width = sash_width - 2 * (frame_width + wing_visible) + overlap
                glass_height = total_height - 2 * (frame_width + wing_visible) + overlap
            else:
                # Фиксирано крило: намаляваме само с касата
                glass_width = sash_width - 2 * frame_width + overlap
                glass_height = total_height - 2 * frame_width + overlap

            # Закръгляме до цели числа
            glass_width = round(glass_width)
            glass_height = round(glass_height)

            # Площ на това крило в кв.м
            area = (glass_width * glass_height) / 1_000_000
            total_area += area

            # Добавяме детайла
            sash_details.append({
                'position': i,
                'type': 'Отваряемо' if is_openable else 'Фиксирано',
                'glass_width': glass_width,
                'glass_height': glass_height,
                'area': round(area, 4)
            })

        # Групираме еднаквите стъклопакети
        grouped = {}
        for detail in sash_details:
            key = (detail['glass_width'], detail['glass_height'], detail['type'])
            if key not in grouped:
                grouped[key] = {
                    'count': 0,
                    'width': detail['glass_width'],
                    'height': detail['glass_height'],
                    'type': detail['type']
                }
            grouped[key]['count'] += 1

        # Форматираме текста
        glass_text_parts = []
        for data in grouped.values():
            if data['count'] > 1:
                glass_text_parts.append(
                    f"{data['count']} бр. × {data['width']}×{data['height']} мм ({data['type']})"
                )
            else:
                glass_text_parts.append(
                    f"{data['width']}×{data['height']} мм ({data['type']})"
                )

        glass_dimensions_text = ", ".join(glass_text_parts)

        return {
            'glass_dimensions': glass_dimensions_text,
            'total_glass_area': round(total_area, 4),
            'sash_width': round(sash_width, 2),
            'details': sash_details
        }

    @staticmethod
    def calculate_material_only_price(product):
        """Изчислява цената само на вложените материали"""
        total = Decimal('0.00')

        # Сумираме цените на всички избрани материали
        for material in product.materials.all():
            total += Decimal(str(material.price_per_unit))

        return float(total)
