import uuid

import os
from shutil import copyfile
from django.db import IntegrityError, models
from django.forms import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from app.managers import CustomUserManager
from django.utils.http import int_to_base36
from smart_selects.db_fields import GroupedForeignKey, ChainedForeignKey
from dirtyfields import DirtyFieldsMixin
from django.core.management import call_command
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
# from notifications.management.commands import save_notification


ID_LENGTH = 30
DEVICE_ID_LENGTH = 15


def id_gen() -> str:
    """Generates random string whose length is `ID_LENGTH`"""
    return int_to_base36(uuid.uuid4().int)[:ID_LENGTH]



class Customer(models.Model):
    id = models.CharField(max_length=ID_LENGTH,
                          primary_key=True, default=id_gen)
    # Field name made lowercase.
    firstname = models.CharField(max_length=50, blank=True, null=True)
    # Field name made lowercase.
    middlename = models.CharField(max_length=50, blank=True, null=True)
    # Field name made lowercase.
    lastname = models.CharField(max_length=50, blank=True, null=True)

    
    mobile = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(
        max_length=254, unique=True, blank=False, null=False)
    picture = models.ImageField(
        upload_to='images/', blank=True, null=True, default='')

    def __str__(self):
        if not self.firstname and not self.lastname:
            return self.email
        return f'{self.firstname} {self.lastname}'

    @property
    def get_photo_url(self):
        if self.picture and hasattr(self.picture, 'url'):
            return self.picture.url
        else:
            return "/static/logo/app_icon.png"

class Gender(models.IntegerChoices):
    MALE = 0, "Male"
    FEMALE = 1, "Female"
    OTHER = 2, "Other"

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(max_length=ID_LENGTH,
                          primary_key=True, default=id_gen, editable=False)
    email = models.EmailField(_("email address"), unique=True, blank=False)    
    firstname = models.CharField(max_length=50, blank=True, null=True)
    # Field name made lowercase.
    middlename = models.CharField(max_length=50, blank=True, null=True)
    # Field name made lowercase.
    lastname = models.CharField(max_length=50, blank=True, null=True)
    gender = models.PositiveSmallIntegerField(choices=Gender.choices, default=Gender.MALE)
    picture = models.ImageField(
        upload_to='images/', blank=True, null=True, default='')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"

    @property
    def get_photo_url(self):
        if self.picture and hasattr(self.picture, 'url'):
            return self.picture.url
        else:
            return "/static/logo/app_icon.png"

    def __str__(self):
        if self.firstname is None and self.lastname is None:
            return self.email
        return f'{self.firstname} {self.lastname}'

class Purpose(models.IntegerChoices):
    WEDDING = 1, "Wedding"
    BAPTISM = 2, "Baptism"
    FUNERAL = 3, "Funeral"


class Status(models.IntegerChoices):
    PENDING = 1, "Pending"
    CONFIRMED = 2, "Confirmed"
    DONE = 3, "Done"
    REJECTED = 4, "Rejected"

def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


class Order(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=False)
    price = models.FloatField()
    discount = models.FloatField()
    quantity = models.SmallIntegerField()
    # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')
    # Field name made lowercase.
    updatedat = models.DateTimeField(
        db_column='updatedAt', blank=True, null=True)

class Product(models.Model):
    name = models.CharField(unique=True, max_length=75, blank=False)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=75, blank=False)
    price = models.FloatField()
    thumbnail = models.ImageField(
        upload_to='services/', blank=True, null=True, default='')

    def __str__(self):
        return self.name
    


class Payment(models.IntegerChoices):
    CASH = 1, "Cash"
    GCASH = 2, "Gcash"
    CARD = 3, "Card"

class AppointmentActions(models.IntegerChoices):
    PENDING = 0, "Pending"
    ACCEPT = 1, "Accept"
    DELETE = 2, "Delete"
    DECLINE = 3, "Decline"

class Service(models.Model):
    name = models.CharField(unique=True, max_length=64, blank=True, default='')
    description = models.TextField(blank=True, null=True)
    price = models.FloatField(default=0)
    thumbnail = models.ImageField(
        upload_to='services/', blank=True, null=True, default='')
    
    def __str__(self):
        return self.name

# Skin Peeling
# Diamond Peel
# Cauteri warts removal
# Laser hair removal

class Appointment(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, default=None)
    date = models.DateTimeField(default=timezone.now, blank=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, blank=True, default=None)
    payment_method = models.PositiveSmallIntegerField(choices=Payment.choices, default=Payment.CASH)
    status = models.PositiveSmallIntegerField(choices=AppointmentActions.choices, default=AppointmentActions.ACCEPT)
    action_message = models.CharField(max_length=256, blank=True, default='')

    def __str__(self):
        return f'{self.id}-{self.customer}-{self.service}'