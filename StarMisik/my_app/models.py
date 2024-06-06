from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.

class Region(models.Model):
    station = models.CharField(max_length=100, primary_key=True)
    city = models.CharField(max_length=100, default='Tokyo')

    def __str__(self):
        return self.station

class Tabelog(models.Model):
    address = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=100)
    station = models.ForeignKey(Region, on_delete=models.CASCADE)
    menu = models.CharField(max_length=200)
    score = models.FloatField()
    num_reviews = models.IntegerField()

    def __str__(self):
        return self.name

class Google(models.Model):
    address = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=100)
    google_score = models.FloatField()
    num_reviews_google = models.IntegerField()

    def __str__(self):
        return self.name

class FinalScore(models.Model):
    address = models.ForeignKey(Tabelog, on_delete=models.CASCADE)
    new_score = models.FloatField()

    def __str__(self):
        return f"{self.address.name} - {self.new_score}"

class CustomUserManager(BaseUserManager):
    def create_user(self, username, age, sex, password=None):
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(username=username, age=age, sex=sex)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, age, sex, password=None):
        user = self.create_user(username, age, sex, password)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    username = models.CharField(max_length=100, unique=True)
    age = models.IntegerField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['age', 'sex']

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

class Favorites(models.Model):
    address = models.ForeignKey(Tabelog, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.address.name}"