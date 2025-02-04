from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.utils import timezone


# Custom user model
class CustomUserManager(UserManager):

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('Username must be set')

        username = self.normalize_email(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(username, password, **extra_fields)


# Override default user class
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(blank=True, default='')
    name = models.CharField(max_length=255, blank=True, default='')
    weight = models.SmallIntegerField(default=0, blank=True, null=True)
    age = models.SmallIntegerField(default=0, blank=True, null=True)
    height = models.SmallIntegerField(default=0, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name


#########################

""" Exercise table model """


class Exercises(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)
    instruction = models.CharField(max_length=255)
    target_muscles = models.CharField(max_length=150)
    rest_between_sets = models.CharField(max_length=100)
    exercise_type = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Exercise"
        verbose_name_plural = "Exercises"


#################


""" Completed exercise table model """


class ExerciseStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    exercise = models.ForeignKey(Exercises, on_delete=models.DO_NOTHING, null=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Exercise status"
        verbose_name_plural = "Status of exercises"


""" User plans model """


class UserPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    exercises = models.ManyToManyField(Exercises, blank=True, default=None)
    frequency = models.SmallIntegerField()
    goals = models.CharField(max_length=255)
    exercise_type = models.CharField(max_length=255, blank=True, null=True)
    daily_duration = models.SmallIntegerField()
    exercises_status = models.ManyToManyField(ExerciseStatus, blank=True, default=None)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "User plan"
        verbose_name_plural = "User plans"



