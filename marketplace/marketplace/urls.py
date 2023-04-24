from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path("", include('app_users.urls')),
    path("", include("django.contrib.auth.urls")),
    path("", include('app_goods.urls')),
    path("", include('app_cart.urls')),
    path("", include('app_orders.urls')),
    path("", include('app_payment.urls')),
    path("admin/", admin.site.urls),
    path("__debug__/", include('debug_toolbar.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
