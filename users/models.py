from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Seeker', 'Seeker'),
        ('Provider', 'Provider'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    favorites = models.ManyToManyField('Gig', related_name='favorited_by', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name', 'phone', 'city', 'role']

    def __str__(self):
        return f"{self.name} ({self.role})"

class Gig(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_posted = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Open')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Changed line

    def __str__(self):
        return self.title

class Application(models.Model):
    gig = models.ForeignKey('Gig', on_delete=models.CASCADE)
    seeker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')
