from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserManager(BaseUserManager):

  def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
    if not email:
        raise ValueError('Users must have an email address')
    now = timezone.now()
    email = self.normalize_email(email)
    user = self.model(
        email=email,
        is_staff=is_staff, 
        is_active=True,
        is_superuser=is_superuser, 
        last_login=now,
        date_joined=now, 
        **extra_fields
    )
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_user(self, email, password, **extra_fields):
    return self._create_user(email, password, False, False, **extra_fields)

  def create_superuser(self, email, password, **extra_fields):
    user=self._create_user(email, password, True, True, **extra_fields)
    return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=254, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)

class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    message = models.TextField()

    def __str__(self):
        return self.name

class Profile(models.Model):

    PRICING_PLAN = [
        ('Free', 'Free'),
        ('Basic', 'Basic'),
        ('Premium', 'Premium'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, default='000000')
    otp_sent_time = models.DateTimeField(default=timezone.now)
    otp_expiry_time = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    storage_limit = models.BigIntegerField(default=5368709120)
    storage_used = models.BigIntegerField(default=0)
    plan = models.CharField(max_length=10, choices=PRICING_PLAN, default='Free')
    plan_start_date = models.DateTimeField(default=timezone.now)
    plan_end_date = models.DateTimeField(default=timezone.now)
    is_payment_done = models.BooleanField(default=False)
    bucket_name = models.CharField(max_length=200, default='')
    keydir = models.TextField(blank=True)

    def __str__(self):
        return self.user.name

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Order(models.Model):
    PaymentStatus = [
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure'),
        ('PENDING', 'Pending'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=PaymentStatus, default='PENDING', null=False, blank=False)
    provider_order_id = models.CharField(max_length=40, null=False, blank=False)
    payment_id = models.CharField(max_length=36, null=False, blank=False)
    signature_id = models.CharField(max_length=128, null=False, blank=False)

    def __str__(self):
        return f"{self.id}-{self.user.name}-{self.status}"
