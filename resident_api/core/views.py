from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import News, Plea
from .serializers import NewsSerializer, PleaSerializer, RegisterSerializer, MyTokenObtainPairSerializer


class NewsViewSet(viewsets.ModelViewSet):
    """
    Жители могут только просматривать новости.
    Админы создают их через админку или отдельно.
    """
    queryset = News.objects.all().order_by('-created_at')
    serializer_class = NewsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # Читать могут все авторизованные, а создавать/редактировать — только админы
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

class PleaViewSet(viewsets.ModelViewSet):
    """
    Жители создают заявки и видят только свои.
    """
    serializer_class = PleaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Если админ - видит всё, если житель - только свои
        if self.request.user.is_staff:
            return Plea.objects.all()
        return Plea.objects.filter(resident=self.request.user)

    def perform_create(self, serializer):
        # При создании привязываем заявку к текущему пользователю
        serializer.save(resident=self.request.user)
    
    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"error": "Только сотрудники могут менять статус"}, 
                            status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny] # Разрешаем всем
    serializer_class = RegisterSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer