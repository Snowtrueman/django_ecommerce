from .filters import set_ordering, get_basic_filters, perform_filters
from django.contrib.auth.models import User
from django.db.models import Prefetch, Count, Q, Min
from django.shortcuts import render
from .forms import ReviewForm
from .models import *
from .utils import TitleMixin
from django.views.generic import TemplateView, DetailView, ListView
from urllib.parse import unquote
from django.utils.encoding import uri_to_iri


class Index(TitleMixin, TemplateView):
    template_name = "app_goods/index.html"
    title = "Megano | Главная"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["selected_cats"] = Categories.objects \
                                       .annotate(min_price=Min("goods__price"), goods_count=Count("goods")) \
                                       .filter(selected=True, goods_count__gt=0)[:3]
        context["top_goods"] = Goods.objects.filter(is_published=True) \
                                   .annotate(sales_number=Count("orders_with_product")).select_related("category") \
                                   .prefetch_related("images").prefetch_related("category__parent") \
                                   .order_by("sort_index").order_by("-sales_number")[:8]
        context["limited_goods"] = Goods.objects.filter(limited=True).select_related("category") \
                                       .prefetch_related("images").order_by("sort_index")[:16]
        return context


class Products(TitleMixin, ListView):
    model = Goods
    template_name = "app_goods/products.html"
    context_object_name = "goods"
    paginate_by = 4
    title = "Megano | Каталог"
    current_ordering = "price"
    ordering_method = "asc"

    def get_queryset(self, **kwargs):
        queryset = Goods.objects.filter(category__slug=self.kwargs["category_slug"], is_published=True) \
            .select_related("category", "category__parent").prefetch_related("images").all()
        return set_ordering(self, queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        if self.kwargs.get("category_slug"):
            context["tags"] = Tags.objects.values("pk", "name").annotate(cnt=Count("id")) \
                .filter(cnt__gte=1, goods_with_tag__category__slug=self.kwargs["category_slug"]).all()
            filters = Params.objects.annotate(param_values=Count("values")) \
                .filter(category__slug=self.kwargs.get("category_slug"), param_values__gt=0, main=True) \
                .prefetch_related(Prefetch("values", queryset=ParamValues.objects.distinct("param", "value") \
                                           .filter(good__in=self.object_list))).all()
            context["filters"] = filters
            context["category_name"] = Categories.get_name_by_slug(slug=self.kwargs.get("category_slug"))
            context["category_slug"] = self.kwargs.get("category_slug")
        context["current_ordering"] = self.current_ordering
        context["ordering_method"] = self.ordering_method
        return context

    def get(self, request, *args, **kwargs):
        if self.kwargs["category_slug"] == "search":
            queryset = Goods.objects.filter(is_published=True)
            queryset = perform_filters(self, queryset)
            self.object_list = set_ordering(self, queryset)
            context = self.get_context_data()
            return render(request, self.template_name, context)
        else:
            queryset = Goods.objects.filter(category__slug=self.kwargs["category_slug"], is_published=True) \
                .select_related("category", "category__parent").prefetch_related("images")

            filter_clauses = get_basic_filters(self)
            for key in request.GET.keys():
                if key.startswith("param_"):
                    category_filters = Params.objects.values("pk").filter(category__slug=self.kwargs["category_slug"]).all()
                    filter_list = [category_filter["pk"] for category_filter in category_filters]
                    extra_filter_clauses = \
                        [Q(params__value__contains=unquote(request.GET.get(f"param_{filter}"))) & Q(params__param__pk=filter)
                                            for filter in filter_list if request.GET.get(f"param_{filter}")]
                    filter_clauses.extend(extra_filter_clauses)

            queryset = perform_filters(self, queryset, filter_clauses)
            self.object_list = set_ordering(self, queryset)
            context = self.get_context_data()
            return render(request, self.template_name, context)


class Product(TitleMixin, DetailView):
    model = Goods
    template_name = "app_goods/product.html"
    context_object_name = "good"
    pk_url_kwarg = "product_id"

    def get_object(self, queryset=None):
        return self.get_queryset().first()

    def get_queryset(self):
        settings = cache.get("settings")
        cache_time = settings.product_cache_time if settings else 60 * 60 * 24 * 14
        queryset = cache.get(f"product_{self.kwargs.get('product_id')}")
        if not queryset:
            queryset = Goods.objects.filter(pk=self.kwargs.get("product_id")) \
                .select_related("category") \
                .prefetch_related("tags") \
                .prefetch_related(Prefetch("images", queryset=ImageGallery.objects.order_by("-main"))) \
                .prefetch_related(Prefetch("reviews", queryset=Reviews.objects.filter(good=self.kwargs["product_id"]))) \
                .prefetch_related("reviews__user").prefetch_related("reviews__user__profile") \
                .prefetch_related(Prefetch("params", queryset=ParamValues.objects.filter(good=self.kwargs["product_id"]))) \
                .prefetch_related("params__param")
            cache.set(f"product_{self.kwargs.get('product_id')}", queryset, cache_time)
        return queryset

    def get_title(self, context):
        return f"Megano | {context['good'].title}"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)

        form = ReviewForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=request.user)
            good = self.object
            text = form.cleaned_data.get("text")
            Reviews.objects.create(user=user, good=good, text=text)
            self.object = self.get_object()
            context = self.get_context_data(**kwargs)
            return render(request, "app_goods/product.html", context=context)
        else:
            context["review_errors"] = form.errors
            return render(request, "app_goods/product.html", context=context)


class Special(TitleMixin, ListView):
    model = Goods
    template_name = "app_goods/special.html"
    title = "Megano | Горячие предложения"
    context_object_name = "goods"
    paginate_by = 4

    def get_queryset(self, **kwargs):
        queryset = Goods.objects.filter(limited=True, is_published=True) \
            .select_related("category").select_related("category__parent").prefetch_related("images").all()
        return set_ordering(self, queryset)

