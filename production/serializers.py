from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    # Това ще покаже името на статуса (напр. "В производство", вместо "in_production")
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Това показва името на клиента (дали е вързан потребител или ръчно въведено)
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'client_name', 'customer_phone', 'delivery_address', 'status', 'status_display', 'created_at']

    def get_client_name(self, obj):
        if obj.customer:
            return obj.customer.username
        return obj.customer_name or "Неизвестен"
