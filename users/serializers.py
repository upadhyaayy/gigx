from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser
from .models import Gig

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'phone', 'city', 'role', 'company_name']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data['phone'],
            city=validated_data['city'],
            role=validated_data['role'],
            company_name=validated_data.get('company_name', '')
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")

class GigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gig
        fields = ['id', 'title', 'description', 'amount', 'created_by', 'date_posted']
        read_only_fields = ['created_by', 'date_posted']
