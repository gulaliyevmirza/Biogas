from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        OPERATOR = 'operator', 'Operator'
        ENGINEER = 'muhendis', 'Mühendis'
        RESEARCHER = 'tedqiqatci', 'Tədqiqatçı'

    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.OPERATOR
    )
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(
        upload_to='profiles/', null=True, blank=True
    )
    company = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'İstifadəçi'
        verbose_name_plural = 'İstifadəçilər'

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN

    @property
    def is_engineer(self):
        return self.role == self.Role.ENGINEER
