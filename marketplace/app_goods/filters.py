from django.db.models import Count, Q


def set_ordering(instance, queryset):
    result = queryset
    if "sort" in instance.request.GET:
        sorting = instance.request.GET.get("sort")
        current_ordering, ordering_method = sorting.split("_")
        match sorting:
            case "popularity_desc":
                result = result.annotate(num_sales=Count("orders_with_product")).order_by("-num_sales")
            case "popularity_asc":
                result = result.annotate(num_sales=Count("orders_with_product")).order_by("num_sales")
            case "price_desc":
                result = result.order_by("-price")
            case "price_asc":
                result = result.order_by("price")
            case "reviews_desc":
                result = result.annotate(num_reviews=Count("reviews")).order_by("-reviews")
            case "reviews_asc":
                result = result.annotate(num_reviews=Count("reviews")).order_by("reviews")
            case "update_desc":
                result = result.order_by("-date_published")
            case "update_asc":
                result = result.order_by("date_published")
        instance.current_ordering = current_ordering
        instance.ordering_method = ordering_method
    return result


def get_basic_filters(instance):
    filter_clauses = []
    if "price" in instance.request.GET:
        price_gte, price_lte = instance.request.GET.get("price").split(";")
        filter_clauses.append(Q(price__gte=int(price_gte)) & Q(price__lte=int(price_lte)))
    if "available" in instance.request.GET:
        filter_clauses.append(Q(amount__gt=0))
    if "free_delivery" in instance.request.GET:
        filter_clauses.append(Q(free_delivery=True))
    if "title" in instance.request.GET:
        title = instance.request.GET.get("title")
        filter_clauses.append(Q(title__icontains=title))
    if "tag" in instance.request.GET:
        tag = instance.request.GET.get("tag")
        filter_clauses.append(Q(tags__in=[tag]))
    return filter_clauses


def perform_filters(instance, queryset, filter_clauses=None):
    if not filter_clauses:
        filter_clauses = get_basic_filters(instance)
    for i in filter_clauses:
        queryset = queryset.filter(i)
    return queryset
