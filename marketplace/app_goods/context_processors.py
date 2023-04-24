from django.db.models import Count
from .models import Categories
from django.core.cache import cache


def menu(request):
    settings = cache.get("settings")
    cache_time = settings.product_cache_time if settings else 60 * 60 * 24 * 14
    menu_categories = cache.get("menu_categories")
    if not menu_categories:
        menu_categories = Categories.objects.annotate(goods_in_subcats=Count("goods")).filter(is_active=True, parent=None) \
            .prefetch_related("subcategories").order_by("sort_index").all()
        cache.set("menu_categories", menu_categories, cache_time)
    return {"menu_categories": menu_categories}
