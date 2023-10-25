from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def created_profile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create a profile when a new user is registered.

    :param sender: Model class. Should always be User in this context.
    :param instance: The actual instance being saved.
    :param created: Boolean; True if a new record was created.
    :param kwargs: Additional keyword arguments.
    """
    if created:
        Profile.objects.create(user=instance)
