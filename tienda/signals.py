from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Solo si el perfil no existe aún (para evitar duplicados)
        UserProfile.objects.get_or_create(user=instance, defaults={
            'role': 'cliente'  # Rol por defecto para usuarios nuevos
        })