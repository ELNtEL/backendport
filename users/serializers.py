from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

# 1️⃣ Serializer for reading user data
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'bio', 'profile_picture', 'date_joined']

# 2️⃣ Serializer for registering a new user
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'password']

    def create(self, validated_data):
        # Use the custom create_user method from your UserManager
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', '')
        )
        return user

# 3️⃣ Serializer for login
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data['user'] = user
        return data
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'full_name', 'bio', 'profile_picture', 'date_joined']
        read_only_fields = ['email','date_joined']
        profile_picture = serializers.ImageField(required=False, allow_null=True)