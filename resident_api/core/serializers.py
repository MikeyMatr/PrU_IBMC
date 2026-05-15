from rest_framework import serializers
from .models import News, Plea
from django.contrib.auth.models import User

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'created_at']

class PleaSerializer(serializers.ModelSerializer):
    # resident заполняем автоматически из текущего пользователя (request.user)
    resident = serializers.ReadOnlyField(source='resident.username')
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Plea
        fields = ['id', 'resident', 'category', 'description', 'status', 'status_display', 'created_at']