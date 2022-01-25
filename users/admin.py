from django.contrib import admin

from .models import UserBot, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email', 'api_key')


@admin.register(UserBot)
class UserBotAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'language_code', 'referral', 'referral_bonus',
                    'referral_balance', 'is_active', 'register_date', 'subscription_is_active',
                    'date_start_subscription', 'date_end_subscription')
    readonly_fields = ('id', 'username', 'first_name', 'last_name', 'language_code', 'referral', 'register_date',
                       'wallets_count', 'date_start_subscription')

    def has_add_permission(self, request, obj=None):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

