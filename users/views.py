from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserProfileSerializer, UserSerializer, RegisterSerializer, LoginSerializer
from .models import User
from django.contrib.auth import authenticate

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_expection=True)
        user = serializer.save

        refresh = RefreshToken.for_user(user)
        return Response({
            "user" : UserSerializer(user).data,
            "refresh" : str(refresh),
            "access" : str(refresh.access_token)
            },status=status.HTTP_201_CREATED),
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwatgs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_expection= true)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
             "user" : UserSerializer(user).data,
            "refresh" : str(refresh),
            "access" : str(refresh.access_token)
        }, status=status.HTTP_200_OK)

class UserView(generics.RetrieveAPIView):
    serializer_class=UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user
    
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user
# Create your views here.
