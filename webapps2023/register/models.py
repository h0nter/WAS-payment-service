from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import CustomUserManager

class Currency(models.TextChoices):
    GBP = 'GBP', 'GBP (British Pound Sterling)'
    USD = 'USD', 'USD (United States Dollar)'
    EUR = 'EUR', 'EUR (Euro)'


# Create your models here - HOW DO I CREATE A CUSTOM USER... ?
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email address', max_length=254, unique=True)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=254)
    currency = models.CharField(max_length=3, choices=Currency.choices, default='')
    is_active = models.BooleanField('active', default=False)
    is_admin = models.BooleanField('admin', default=False)
    change_password = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [email, username, first_name, last_name]

    objects = CustomUserManager()

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin or self.is_superuser


class Balance(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.GBP)
    amount = models.DecimalField(max_digits=19, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.amount} {self.currency}'
