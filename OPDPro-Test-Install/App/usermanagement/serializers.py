# usermanagement/serializers.py
from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'mobile_number', 'first_name', 'last_name', 
            'date_of_birth', 'gender', 'staff_role', 'is_active', 'is_staff', 'date_joined'
        ]
        read_only_fields = ['id', 'is_active', 'is_staff', 'date_joined']
