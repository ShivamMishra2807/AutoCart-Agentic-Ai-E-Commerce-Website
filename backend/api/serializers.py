from rest_framework import serializers
from .models import (
    User, Category, Product, Coupon, Seller, Order,
    Store, StoreInventory, InventoryReservation,
    SellerApplication, SellerApplicationAudit,
    OrderFulfillment, AgentTask, AgentExecutionLog
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone', 'role', 'status', 'joinedDate', 'ordersCount', 'totalSpent', 'addresses']
        read_only_fields = ['id', 'joinedDate']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'

class StoreInventorySerializer(serializers.ModelSerializer):
    productName = serializers.CharField(source='product.name', read_only=True)
    productBrand = serializers.CharField(source='product.brand', read_only=True)
    productPrice = serializers.FloatField(source='product.price', read_only=True)
    productImages = serializers.JSONField(source='product.images', read_only=True)
    storeName = serializers.CharField(source='store.name', read_only=True)
    storeCity = serializers.CharField(source='store.city', read_only=True)

    class Meta:
        model = StoreInventory
        fields = '__all__'

class InventoryReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryReservation
        fields = '__all__'

class SellerApplicationAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerApplicationAudit
        fields = '__all__'

class SellerApplicationSerializer(serializers.ModelSerializer):
    audit_logs = SellerApplicationAuditSerializer(many=True, read_only=True)

    class Meta:
        model = SellerApplication
        fields = '__all__'

class OrderFulfillmentSerializer(serializers.ModelSerializer):
    storeName = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = OrderFulfillment
        fields = '__all__'

class AgentExecutionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentExecutionLog
        fields = '__all__'

class AgentTaskSerializer(serializers.ModelSerializer):
    logs = AgentExecutionLogSerializer(many=True, read_only=True)

    class Meta:
        model = AgentTask
        fields = '__all__'
