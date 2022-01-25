from django.db import models
from django.utils.timezone import now
from users.models import UserBot, TransactionFilter

WalletChain = (
        ('eth', 'eth'),
        ('bsc', 'bsc'),
        ('polygon', 'polygon'),
    )

TransactionType = (
    ('native', 'native'),
    ('token', 'token'),
    ('nft', 'nft'),
)


class Wallet(TransactionFilter):

    address = models.CharField(max_length=100)
    user = models.ForeignKey(UserBot, related_name="wallets", on_delete=models.CASCADE)
    chain = models.CharField(max_length=100, choices=WalletChain)
    description = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(default=now)
    last_tx_timestamp = models.IntegerField()
    last_tx_block_number = models.IntegerField(blank=True, null=True)
    show_balance = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.address}'

    def save(self, *args, **kwargs):
        self.last_tx_timestamp = int(now().timestamp())
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ('-created_at',)


class StatsWallet(models.Model):
    address = models.CharField(max_length=100)
    wallet = models.ForeignKey(Wallet, related_name="stats", on_delete=models.CASCADE)
    description = models.CharField(max_length=500, blank=True, null=True)
    start_timestamp = models.IntegerField(blank=True, null=True)
    end_timestamp = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.address}'

    class Meta:
        unique_together = (("address", "wallet"),)
        ordering = ('-created_at',)


class TokenContract(models.Model):
    token_address = models.CharField(max_length=100)
    chain = models.CharField(max_length=50, choices=WalletChain)
    name = models.CharField(max_length=100, blank=True, null=True)
    symbol = models.CharField(max_length=50, blank=True, null=True)
    decimals = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.token_address}'

    class Meta:
        unique_together = (("token_address", "chain"),)


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, related_name="transactions", on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=TransactionType)
    token_contract = models.ForeignKey(TokenContract, blank=True, null=True, on_delete=models.PROTECT)
    hash = models.CharField(max_length=100, blank=True, null=True)
    to_address = models.CharField(max_length=100, blank=True, null=True)
    from_address = models.CharField(max_length=100, blank=True, null=True)
    tx_fee = models.CharField(max_length=100, blank=True, null=True)
    value = models.CharField(max_length=100, blank=True, null=True)
    native_price = models.DecimalField(decimal_places=10, max_digits=20, blank=True, null=True)
    token_price = models.DecimalField(decimal_places=10, max_digits=20, blank=True, null=True)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.hash}'

    class Meta:
        ordering = ('-created_at',)
