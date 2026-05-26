from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import News, Plea, Profile

# 1. Настройка инлайна профиля (чтобы видеть адрес и роль внутри страницы пользователя)
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Дополнительная информация (Профиль)'
    fields = ('role', 'address', 'apartment')

# 2. Настройка новой админки для Пользователя
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    # Добавим отображение роли прямо в списке пользователей
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    
    def get_role(self, obj):
        return obj.profile.get_role_display()
    get_role.short_description = 'Роль'

# Перерегистрируем стандартный User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 3. Настройка админки Новостей
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'content')

# 4. Настройка админки Заявок (сделаем её максимально мощной)
@admin.register(Plea)
class PleaAdmin(admin.ModelAdmin):
    # Добавляем адрес, квартиру и исполнителя в список
    list_display = ('id', 'resident', 'category', 'address', 'apartment', 'status', 'executor', 'created_at')
    
    # Позволяем быстро менять статус и мастера прямо из списка
    list_editable = ('status', 'executor')
    
    # Фильтры справа
    list_filter = ('status', 'category', 'created_at')
    
    # Поиск по жителю и описанию
    search_fields = ('resident__username', 'description', 'address')

# Оставляем регистрацию Profile отдельно (на случай, если нужно быстро найти профиль)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'address', 'apartment')
    list_filter = ('role',)