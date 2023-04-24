from django.contrib import admin
from django.contrib.admin.views.main import ChangeList

from .models import *


class OrderDetailInline(admin.StackedInline):
    model = OrderDetail
    extra = 0


@admin.action(description="Восстановить удалённые записи")
def restore_item(modeladmin, request, queryset):
    for item in queryset:
        for product in OrderDetail.all_objects.filter(deleted_at__isnull=False).filter(order_num=item.pk).all():
            product.restore()
        item.restore()


class CustomChangeList(ChangeList):
    def get_queryset(self, request):
        if "deleted" in request.GET:
            return Order.all_objects.filter(deleted_at__isnull=False)
        else:
            return super().get_queryset(request)


class OrderAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "delivery_type", "payment_type", "payment_status", "status", "delivery_price",)
    list_display_links = ("pk",)
    list_select_related = ("user", "payment_type",)
    readonly_fields = ("date",)
    fieldsets = [
        ("Базовая информация о заказе", {"fields": ["user", "delivery_type", "total_price", "payment_type",
                                                    "payment_status", "delivery_price", "city", "address",
                                                    "status", "date"],
                                         })]
    inlines = [OrderDetailInline]
    actions = [restore_item]

    def delete_queryset(self, request, queryset):
        for item in queryset:
            for product in item.order_products.all():
                product.delete()
            item.delete()

    def get_changelist(self, request, **kwargs):
        return CustomChangeList


class PaymentAdmin(admin.ModelAdmin):
    list_display = ("pk", "type", "slug")
    list_display_links = ("pk",)


admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
