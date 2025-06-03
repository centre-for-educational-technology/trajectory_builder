from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image
from django.dispatch import receiver
from django.db.models.signals import post_save
import os

from django.contrib.auth import get_user_model
User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile whenever a User is created"""
    if created:
        profile = Profile.objects.create(user=instance)
        
        # Handle default avatar image
        default_path = os.path.join('static', 'default.jpg')
        if os.path.exists(default_path):
            with open(default_path, 'rb') as f:
                profile.avatar.save('default.jpg', f, save=True)
        
        # Resize the image (replicating your save() logic)
        try:
            img = Image.open(profile.avatar.path)
            if img.height > 100 or img.width > 100:
                new_img = (100, 100)
                img.thumbnail(new_img)
                img.save(profile.avatar.path)
        except:
            pass  # Handle cases where image processing fails


class Profile(models.Model):
    """This model extends Django User model with a profile picture.

    """
    # one-to-one mapping with Django User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # profile picture for each user
    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')

    
    
    def __str__(self):
        """This function returns user's name.

        Returns:
            str: name of user
        """
        return self.user.first_name

    def save(self, *args, **kwargs):
        """This function resize and save the image on saving user's data.
        """
        super().save()

        # open profile pic
        img = Image.open(self.avatar.path)

        # size check
        if img.height > 100 or img.width > 100:
            new_img = (100, 100)
            img.thumbnail(new_img)
            # save image
            img.save(self.avatar.path)