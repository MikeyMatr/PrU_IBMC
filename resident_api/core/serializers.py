from rest_framework import serializers
from .models import News, Plea, Profile 
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
        fields = ['id', 'resident', 'category','address', 'apartment', 'description', 'status', 'status_display', 'created_at']


# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'password', 'email']

#     def create(self, validated_data):
#         # Используем create_user, чтобы пароль захешировался
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             password=validated_data['password'],
#             email=validated_data.get('email', '')
#         )
#         return user
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # Добавляем поля, которые не входят в модель User, но нужны для Profile
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)
    apartment = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'address', 'apartment']

    def create(self, validated_data):
        # Извлекаем адресные данные перед созданием пользователя
        address = validated_data.pop('address', '')
        apartment = validated_data.pop('apartment', '')
        
        # Создаем пользователя
        user = User.objects.create_user(**validated_data)
        
        # Обновляем автоматически созданный профиль (созданный сигналом)
        profile, created = Profile.objects.get_or_create(user=user)
        profile.address = address
        profile.apartment = apartment
        profile.save()
        
        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Убедитесь, что эта строка есть!
        data['role'] = self.user.profile.role 
        data['is_staff'] = self.user.is_staff
        return data