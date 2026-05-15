from django.contrib import admin
from .models import News, Plea

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')

@admin.register(Plea)
class PleaAdmin(admin.ModelAdmin):
    list_display = ('id', 'resident', 'category', 'status', 'created_at')
    list_filter = ('status', 'category')
    # Разрешаем менять статус прямо из списка
    list_editable = ('status',) 