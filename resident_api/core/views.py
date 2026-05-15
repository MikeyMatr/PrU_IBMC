from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import News, Plea
from .serializers import NewsSerializer, PleaSerializer

class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Жители могут только просматривать новости.
    Админы создают их через админку или отдельно.
    """
    queryset = News.objects.all().order_by('-created_at')
    serializer_class = NewsSerializer
    permission_classes = [permissions.IsAuthenticated]

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