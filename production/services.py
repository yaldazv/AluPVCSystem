class ProductionService:
    @staticmethod
    def calculate_dimensions_and_areas(product):
        """
        Изчислява площи, като взема офсета ДИНАМИЧНО от категорията на продукта.
        """
        # Вземаме офсета директно от базата данни:
        offset = product.category.system_offset

        # Превръщаме размерите в чист светъл отвор
        net_width = max(0, product.width - (offset * 2))
        net_height = max(0, product.height - (offset * 2))

        # Обща площ на пълнежа в кв.м.
        net_fill_area = (net_width * net_height) / 1_000_000

        # Разпределяме площта според процента стъкло
        glass_area = net_fill_area * (product.glass_percentage / 100)
        panel_area = net_fill_area - glass_area

        return {
            'glass_area': round(glass_area, 2),
            'panel_area': round(panel_area, 2),
            'net_width': net_width,
            'net_height': net_height
        }

    @staticmethod
    def calculate_material_only_price(product):
        """
        Изчислява цената на продукта КАТО СУМА ОТ ЦЕНИТЕ НА МАТЕРИАЛИТЕ.
        Не включва труд, а само обков и консумативи от ManyToMany връзката.
        """
        total_price = 0

        # Вземаме всички материали, прикачени към продукта
        # (Дръжки, панти, механизми, мрежи и т.н.)
        selected_materials = product.materials.all()

        for material in selected_materials:
            # Тук приемаме, че в Inventory/Material има поле price_per_unit
            total_price += float(material.price_per_unit)

        return round(total_price, 2)

    @staticmethod
    def get_production_report(product):
        """
        Генерира пълна справка за производството (за работника).
        """
        areas = ProductionService.calculate_dimensions_and_areas(product)

        return {
            'type': product.get_product_type_display(),
            'dimensions': f"{product.width} x {product.height} mm",
            'glass_needed': f"{areas['glass_area']} sqm",
            'panel_needed': f"{areas['panel_area']} sqm",
            'materials_list': [m.name for m in product.materials.all()]
        }