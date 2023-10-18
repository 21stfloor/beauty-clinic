from rest_framework import serializers

from .models import Appointment, Customer, CustomUser


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

# class AppointmentSerializer(serializers.Serializer):
#     label = serializers.CharField()
#     data = serializers.ListField(child=serializers.IntegerField())
#     backgroundColor = serializers.CharField()
#     borderColor = serializers.CharField()
#     borderWidth = serializers.IntegerField()

class ServiceAppointmentCountSerializer(serializers.Serializer):
    service__name = serializers.CharField()
    month = serializers.IntegerField()
    count = serializers.IntegerField()


class GenderDistributionSerializer(serializers.Serializer):
    gender = serializers.CharField()
    count = serializers.IntegerField()