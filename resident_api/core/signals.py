from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import News, Plea
from .services import send_push_notification

@receiver(post_save, sender=News)
def notify_all_residents_news(sender, instance, created, **kwargs):
    """При создании новости уведомляем всех пользователей"""
    if created:
        residents = User.objects.all()
        for resident in residents:
            send_push_notification(
                resident, 
                "Новая новость в ЖЭУ", 
                instance.title
            )

@receiver(post_save, sender=Plea)
def notify_resident_plea_status(sender, instance, created, **kwargs):
    """При изменении статуса заявки уведомляем только её автора"""
    if not created:  # Нас интересует только изменение уже существующей заявки
        send_push_notification(
            instance.resident, 
            "Статус вашей заявки изменен", 
            f"Заявка #{instance.id} теперь в статусе: {instance.get_status_display()}"
        )
