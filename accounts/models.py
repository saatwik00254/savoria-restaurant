from django.db import models
from django.contrib.auth.models import User

ROLE_CHOICES = [
    ('customer', 'Customer'),
    ('staff', 'Staff'),
    ('admin', 'Admin'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def is_admin_or_staff(self):
        return self.role in ('admin', 'staff')
