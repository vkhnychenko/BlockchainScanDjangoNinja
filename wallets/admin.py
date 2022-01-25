from django.contrib import admin

from .models import Wallet, StatsWallet, Transaction, TokenContract


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'address', 'chain', 'user')


@admin.register(StatsWallet)
class StatsAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'wallet', 'description', 'start_timestamp', 'end_timestamp')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'hash')


@admin.register(TokenContract)
class TokenContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'token_address')
