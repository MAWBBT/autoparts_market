from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'password']

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('Пароль должен быть минимум 8 символов')
        return value

    def validate_email(self, value):
        # OGR из методички: символ @
        if '@' not in value:
            raise serializers.ValidationError('Email должен содержать символ @')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        return User.objects.create_user(password=password, **validated_data)

