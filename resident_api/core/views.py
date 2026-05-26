from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from django.utils import timezone

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
        user = self.request.user
        
        # 1. Получаем то, что пришло из формы на сайте
        raw_address = self.request.data.get('address', '')
        raw_apartment = self.request.data.get('apartment', '')

        # 2. Получаем то, что сохранено в профиле
        try:
            profile_address = user.profile.address
            profile_apartment = user.profile.apartment
        except Exception:
            profile_address = ""
            profile_apartment = ""

        # 3. ЛОГИКА ВЫБОРА: Если в форме пусто — берем из профиля
        final_address = raw_address.strip() if raw_address and raw_address.strip() else profile_address
        final_apartment = raw_apartment.strip() if raw_apartment and raw_apartment.strip() else profile_apartment

        # ТЕРМИНАЛ: Печатаем для проверки
        print(f"--- АВТОЗАПОЛНЕНИЕ ДЛЯ {user.username} ---")
        print(f"Из формы: '{raw_address}', Из профиля: '{profile_address}'")
        print(f"ИТОГ: '{final_address}'")

        # 4. Сохраняем с финальными данными
        serializer.save(
            resident=user,
            address=final_address,
            apartment=final_apartment
        )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def stats(self, request):
        user = request.user
        role = getattr(user.profile, 'role', 'resident')
        today = timezone.now().date()

        # Базовый запрос (все заявки)
        queryset = Plea.objects.all()

        # Если это мастер, фильтруем статистику только по его категории
        if role == 'plumber':
            queryset = queryset.filter(category='plumber')
        elif role == 'electrician':
            queryset = queryset.filter(category='electrician')
        elif not user.is_staff and role != 'manager':
            return Response({"error": "Нет доступа"}, status=403)

        # Считаем данные на основе отфильтрованного queryset
        data = {
            "new": queryset.filter(status='new').count(),
            "in_progress": queryset.filter(status='in_progress').count(),
            "completed_today": queryset.filter(status='completed', updated_at__date=today).count(),
            "total": queryset.count(),
        }
        return Response(data)