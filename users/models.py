from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


# class Role(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    # We use the default 'is_active' from AbstractUser
    
    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # If this is a superuser, force their role to 'admin'
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)
