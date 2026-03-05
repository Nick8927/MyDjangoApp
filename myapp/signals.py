from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Order
import threading


@receiver(post_save, sender=User)
def notify_admin_about_new_user(sender, instance, created, **kwargs):
    if created:
        local_time = timezone.localtime(instance.date_joined)

        subject = "Новая регистрация"

        message = (
            f"Зарегистрирован новый пользователь:\n\n"
            f"Username: {instance.username}\n"
            f"Дата регистрации: {local_time.strftime('%d.%m.%Y %H:%M:%S')}"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True,
        )


@receiver(post_save, sender=Order)
def notify_admin_about_new_order(sender, instance, created, **kwargs):
    if created:
        local_time = timezone.localtime(instance.created_at)

        subject = "Новый заказ"

        message = (
            f"Создан новый заказ:\n\n"
            f"Номер заказа: {instance.order_number}\n"
            f"ФИО: {instance.name}\n"
            f"Телефон: {instance.phone}\n"
            f"Сумма заказа: {instance.total_price} руб.\n"
            f"Дата создания: {local_time.strftime('%d.%m.%Y %H:%M:%S')}"
        )

        threading.Thread(
            target=send_email_async,
            args=(subject, message)
        ).start()


def send_email_async(subject, message):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
        fail_silently=True,
    )
