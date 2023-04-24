from .models import Settings
from django.core.cache import cache


def settings(request):
    settings = cache.get("settings")
    cache_time = settings.product_cache_time if settings else 60 * 60 * 24 * 14
    if not settings:
        settings = Settings.objects.first()
        cache.set("settings", settings, cache_time)
    return {"settings": settings}
