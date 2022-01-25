from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ninja import NinjaAPI

from users.services import ApiKey
from users.views import user_router
from wallets.views import wallet_router


api = NinjaAPI(version='0.2.0', auth=ApiKey())

api.add_router("users/", user_router)
api.add_router("wallet/", wallet_router)


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", api.urls),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
