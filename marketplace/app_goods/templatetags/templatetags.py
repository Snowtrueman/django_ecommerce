from django import template
from django.template import Context
register = template.Library()


@register.simple_tag
def define(val=None):
    return val


@register.simple_tag
def make_order_by_url(url, default_ordering, current_ordering, current_method):
    cut_place_page = url.find("page")
    if cut_place_page != -1:
        url = url[:cut_place_page - 1]
    cut_place_sort = url.find("sort")
    if cut_place_sort != -1:
        url = url[:cut_place_sort - 1]
    composite = "?" in url
    url = url + "&sort=" if composite else url + "?sort="
    if default_ordering != current_ordering:
        url += f"{default_ordering}_asc"
    else:
        if current_method == "asc":
            url += f"{default_ordering}_desc"
        else:
            url += f"{default_ordering}_asc"
    return url


@register.simple_tag
def make_order_by_class(default_ordering, current_ordering, current_method):
    if default_ordering != current_ordering:
        return
    else:
        if current_method == "asc":
            return "Sort-sortBy_dec"
        else:
            return "Sort-sortBy_inc"


@register.simple_tag
def make_pagination_url(url, page):
    cut_place = url.find("page")
    if cut_place != -1:
        url = url[:cut_place - 1]
    composite = "?" in url
    return url + f"&page={page}" if composite else url + f"?page={page}"


@register.simple_tag
def receive_get_param(request, value):
    return request.GET.get("param_"+str(value))


@register.simple_tag
def get_min_price(request):
    min_price = request.GET.get("price").split(";")[0] if request.GET.get("price") else "10"
    return min_price


@register.simple_tag
def get_max_price(request):
    max_price = request.GET.get("price").split(";")[1] if request.GET.get("price") else "1000000"
    return max_price


@register.simple_tag(name="get_product_quantity_error", takes_context=True)
def get_product_quantity_error(context, produck_pk):
    name = f"error_{produck_pk}"
    context = Context(context)
    result = context.get(name)
    return result if result else ""