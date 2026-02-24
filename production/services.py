from decimal import Decimal


class ProductionService:


    @staticmethod
    def calculate_glass_dimensions(product):
        # Вземаме размерите на целия прозорец
        total_width = Decimal(str(product.width))
        total_height = Decimal(str(product.height))

        # Брой части
        total_sashes = product.total_sashes
        openable_sashes = product.openable_sashes

        # Ширина на една част (ако има повече от 1, делим равно)
        sash_width = total_width / total_sashes if total_sashes > 0 else total_width

        sash_details = []
        total_area = Decimal('0.00')

        FIX_DEDUCTION = Decimal('45')  # Намаление от външен габарит до стъкло за ФИКС
        SASH_DEDUCTION = Decimal('105')  # Намаление от външен габарит до стъкло за КРИЛО

        for i in range(total_sashes):
            # Определяме дали текущата част е отваряема (първо броим отваряемите)
            if i < openable_sashes:
                # ЛОГИКА ЗА КРИЛО (Отваряемо)
                g_width = sash_width - SASH_DEDUCTION
                g_height = total_height - SASH_DEDUCTION
                g_type = "Крило (отваряемо)"
            else:
                # ЛОГИКА ЗА ФИКС (Неотваряемо)
                g_width = sash_width - FIX_DEDUCTION
                g_height = total_height - FIX_DEDUCTION
                g_type = "Фикс (неотваряемо)"

            # Изчисляваме площта на това парче в кв.м.
            area = (g_width * g_height) / Decimal('1000000')
            total_area += area

            sash_details.append({
                'glass_width': round(g_width, 0),
                'glass_height': round(g_height, 0),
                'type': g_type
            })

        # Группираме за текста (същата логика като твоята досега)
        grouped = {}
        for detail in sash_details:
            key = (detail['glass_width'], detail['glass_height'], detail['type'])
            if key not in grouped:
                grouped[key] = {'count': 0, 'w': detail['glass_width'], 'h': detail['glass_height'],
                                't': detail['type']}
            grouped[key]['count'] += 1

        glass_text_parts = []
        for d in grouped.values():
            prefix = f"{d['count']} бр. × " if d['count'] > 1 else ""
            glass_text_parts.append(f"{prefix}{int(d['w'])}×{int(d['h'])} мм ({d['t']})")

        return {
            'glass_dimensions': ", ".join(glass_text_parts),
            'total_glass_area': round(total_area, 4),
            'sash_width': round(sash_width, 2),
            'details': sash_details  # Връщаме детайлния списък
        }


    @staticmethod
    def calculate_material_only_price(product):
        total = Decimal('0.00')


        for material in product.materials.all():
            total += Decimal(str(material.price_per_unit))

        return float(total)
