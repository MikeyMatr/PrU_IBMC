from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import News, Plea
from .serializers import (
    NewsSerializer, 
    PleaSerializer, 
    RegisterSerializer, 
    MyTokenObtainPairSerializer
)

class MyTokenObtainPairView(TokenObtainPairView):
    """Логин с возвратом роли пользователя"""
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class NewsViewSet(viewsets.ModelViewSet):
    """Новости: чтение для всех, создание для админов"""
    queryset = News.objects.all().order_by('-created_at')
    serializer_class = NewsSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class PleaViewSet(viewsets.ModelViewSet):
    """Заявки: умная фильтрация по ролям"""
    serializer_class = PleaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # Защита от отсутствия профиля
        try:
            role = user.profile.role
        except Exception:
            role = 'manager' if user.is_staff else 'resident'

        print(f"--- DEBUG: Запрос от {user.username} | Роль: {role} ---")

        # 1. Менеджеры и Админы
        if user.is_staff or role == 'manager':
            return Plea.objects.all().order_by('-created_at')
        
        # 2. Сантехники
        if role == 'plumber':
            return Plea.objects.filter(category='plumber').order_by('-created_at')
        
        # 3. Электрики
        if role == 'electrician':
            return Plea.objects.filter(category='electrician').order_by('-created_at')
        
        # 4. Жители
        return Plea.objects.filter(resident=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(resident=self.request.user)