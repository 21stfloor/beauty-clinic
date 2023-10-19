from rest_framework import serializers

from .models import Appointment, Customer, CustomUser, Order, Product, Service


class CustomerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'picture')

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'email', 'firstname',
                  'middlename', 'lastname', 'mobile', 'picture')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for key, value in data.items():
            try:
                if not value:
                    data[key] = ""
            except KeyError:
                pass
        return data


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'picture',
                  'firstname', 'middlename', 'lastname')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for key, value in data.items():
            try:
                if not value:
                    data[key] = ""
            except KeyError:
                pass
        return data

class ServiceAppointmentCountSerializer(serializers.Serializer):
    service__name = serializers.CharField()
    month = serializers.IntegerField()
    count = serializers.IntegerField()


class GenderDistributionSerializer(serializers.Serializer):
    gender = serializers.CharField()
    count = serializers.IntegerField()

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'
    
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['customer', 'price', 'discount', 'payment_method', 'date', 'product', 'quantity']  # List the fields you want to include

    def create(self, validated_data):
        # You can perform additional actions here if needed
        return Order.objects.create(**validated_data)