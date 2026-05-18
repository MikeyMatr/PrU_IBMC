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


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        # Используем create_user, чтобы пароль захешировался
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user