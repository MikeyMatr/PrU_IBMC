from django.db import models
from django.contrib.auth.models import User

class News(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Текст новости")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

    def __str__(self):
        return self.title
    
class Profile(models.Model):
    ROLE_CHOICES = [
        ('resident', 'Житель'),
        ('plumber', 'Сантехник'),
        ('electrician', 'Электрик'),
        ('manager', 'Диспетчер/Админ'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Plea(models.Model):
    TYPE_CHOICES = [
        ('plumber', 'Сантехник'),
        ('electrician', 'Электрик'),
    ]
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
    ]

    resident = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pleas')
    category = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Тип мастера")
    description = models.TextField(verbose_name="Описание проблемы")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"Заявка #{self.id} - {self.get_category_display()}"
