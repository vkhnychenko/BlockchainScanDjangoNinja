from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
import secrets


class TransactionFilter(models.Model):
    native_transfer = models.BooleanField(default=True)
    token_transfer = models.BooleanField(default=True)
    nft_transfer = models.BooleanField(default=True)
    limit_native = models.IntegerField(blank=True, null=True)
    limit_tokens = models.IntegerField(blank=True, null=True)
    limit_currency = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    """ Custom model user"""
    api_key = models.CharField(max_length=100, default=secrets.token_urlsafe(25))


class UserBot(TransactionFilter):
    id = models.IntegerField(primary_key=True, unique=True)
    username = models.CharField(max_length=100, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    language_code = models.CharField(max_length=10, blank=True, null=True)
    referral = models.IntegerField(blank=True, null=True)
    referral_bonus = models.IntegerField(default=10)
    referral_balance = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    register_date = models.DateTimeField(default=now)
    subscription_is_active = models.BooleanField(default=False)
    date_start_subscription = models.DateTimeField(blank=True, null=True)
    date_end_subscription = models.DateTimeField(blank=True, null=True)
    available_wallets_count = models.IntegerField(default=2, null=True)
    wallets_count = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.id}'
