import requests

def send_push_notification(user, title, message):
    """
    Функция для отправки уведомления.
    В будущем здесь будет вызов Firebase Cloud Messaging (FCM).
    """
    print(f"\n--- ОТПРАВКА PUSH (Firebase) ---")
    print(f"Кому: {user.username} (ID: {user.id})")
    print(f"Заголовок: {title}")
    print(f"Текст: {message}")
    print(f"---------------------------------\n")
    
    # Пример того, как это будет выглядеть с реальным Firebase:
    # requests.post('https://fcm.googleapis.com/fcm/send', headers=headers, json=payload)