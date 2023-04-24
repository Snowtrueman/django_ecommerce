from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from .models import *


class ParamsInline(admin.StackedInline):
    model = Params
    extra = 0


def restore_params_values(subcategory):
    params = Params.all_objects.filter(deleted_at__isnull=False).filter(category=subcategory.pk).all()
    if params:
        for param in params:
            params_values = ParamValues.all_objects.filter(deleted_at__isnull=False).filter(param=param.pk).all()
            if params_values:
                for param_value in params_values:
                    param_value.restore()
            param.restore()


def restore_goods_images(subcategory):
    goods = Goods.all_objects.filter(deleted_at__isnull=False).filter(category=subcategory.pk).all()
    if goods:
        for good in goods:
            images = ImageGallery.all_objects.filter(deleted_at__isnull=False).filter(good=good.pk).all()
            if images:
                for image in images:
                    image.restore()
            good.restore()


def restore_subcategories(category):
    subcategories = Categories.all_objects.filter(deleted_at__isnull=False).filter(parent=category.pk).all()
    if subcategories:
        for subcategory in subcategories:
            restore_subcategories(subcategory)
            restore_params_values(subcategory)
            restore_goods_images(subcategory)
            subcategory.restore()
    restore_params_values(category)
    restore_goods_images(category)
    return


@admin.action(description="Восстановить удалённые категории")
def restore_categories(modeladmin, request, queryset):
    for category in queryset:
        restore_subcategories(category)
        category.restore()


class CategoriesChangeList(ChangeList):
    def get_queryset(self, request):
        if "deleted" in request.GET:
            return Categories.all_objects.filter(deleted_at__isnull=False)
        else:
            return super().get_queryset(request)


class CategoriesAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "selected", "sort_index", "parent",)
    list_display_links = ("title",)
    list_editable = ("is_active", "selected",)
    list_select_related = True
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = [
        ("Базовая информация о категории", {"fields": ["title", "is_active", "selected", "sort_index", "parent",
                                                       "slug", "icon", "img"]})]
    inlines = [ParamsInline]
    actions = [restore_categories]

    @staticmethod
    def delete_params_goods_images(subcategory):
        for param in subcategory.params.all():
            for param_value in param.values.all():
                param_value.delete()
            param.delete()
        for good in subcategory.goods.all():
            for image in good.images.all():
                image.delete()
            good.delete()

    def delete_subcategories(self, category):
        if category.subcategories.all():
            for subcategory in category.subcategories.all():
                self.delete_subcategories(subcategory)
                self.delete_params_goods_images(subcategory)
                subcategory.delete()
        self.delete_params_goods_images(category)
        return

    def delete_queryset(self, request, queryset):
        for category in queryset:
            self.delete_subcategories(category)
            category.delete()

    def get_changelist(self, request, **kwargs):
        return CategoriesChangeList


class TagsAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_display_links = ("name",)


class ParamValuesInline(admin.StackedInline):
    model = ParamValues
    extra = 0

    def get_queryset(self, request):
        return super(ParamValuesInline, self).get_queryset(request).select_related("param") \
            .prefetch_related("param__category")


class ImageGalleryInline(admin.StackedInline):
    model = ImageGallery
    extra = 0


@admin.action(description="Восстановить удалённые товары")
def restore_goods(modeladmin, request, queryset):
    for good in queryset:
        for image in ImageGallery.all_objects.filter(deleted_at__isnull=False).filter(good=good.pk).all():
            image.restore()
        good.restore()


class GoodsChangeList(ChangeList):
    def get_queryset(self, request):
        if "deleted" in request.GET:
            return Goods.all_objects.filter(deleted_at__isnull=False).select_related("category")
        else:
            return super().get_queryset(request).select_related("category")


class GoodsAdmin(admin.ModelAdmin):
    list_display = ("part_num", "title", "price", "free_delivery", "amount", "sort_index", "date_published",
                    "category", "is_published",)
    list_display_links = ("part_num", "title",)
    list_editable = ("free_delivery", "is_published",)
    readonly_fields = ("date_published",)
    fieldsets = [
        ("Базовая информация о товаре", {"fields": ["part_num", "title", "price", "short_description", "free_delivery",
                                                    "amount", "description", "limited", "tags",
                                                    "sort_index", "date_published", "category", "is_published", ]})]
    inlines = [ParamValuesInline, ImageGalleryInline]
    actions = [restore_goods]

    def delete_queryset(self, request, queryset):
        for good in queryset:
            for image in good.images.all():
                image.delete()
            good.delete()

    def get_changelist(self, request, **kwargs):
        return GoodsChangeList


class ReviewsAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "good", "text", "date_published",)
    list_display_links = ("pk",)


admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(Reviews, ReviewsAdmin)
