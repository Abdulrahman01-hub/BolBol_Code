from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Advertisement
from .tasks import send_notification_email


@receiver(post_save, sender=Advertisement)
def send_email_on_new_ad(sender, instance, created, **kwargs):
    if created:
        subject = "Yeni İlan Oluşturuldu!"
        message = f"Yeni ilan oluşturuldu: {instance.title}\nDetaylar: {instance.description}"
        recipient_list = ["barbarossa.123456.1@gmail.com"]

        send_notification_email.delay(subject, message, recipient_list)