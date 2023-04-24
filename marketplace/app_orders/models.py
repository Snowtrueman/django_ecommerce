from django.db import models
import datetime


class SoftDeleteManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.deleted = kwargs.pop("deleted", False)
        super(SoftDeleteManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if not self.deleted:
            return super().get_queryset().filter(deleted_at__isnull=True)
        else:
            return super().get_queryset().filter(deleted_at__isnull=False)


class SoftDeleteModel(models.Model):

    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    objects = SoftDeleteManager()
    deleted_objects = SoftDeleteManager(deleted=True)
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = datetime.datetime.now()
        self.save()

    def restore(self):
        self.deleted_at = None
        self.save()

    class Meta:
        abstract = True


class Order(SoftDeleteModel):
    STATUSES = (
        ("created", "Не оплачен"),
        ("paid", "Оплачен"),
        ("delivery", "В доставке"),
        ("success", "Завершен"),
        ("canceled", "Отменен"),
    )

    PAYMENT_STATUSES = (
        ("OK", "Оплата прошла успешно."),
        ("invalid_number", "Указанный номер карты недействителен."),
        ("card_expired", "Срок действия карты истёк."),
        ("insufficient funds", "На карте недостаточно средств."),
        ("processing_error", "Ошибка на стороне платёжной системы."),
        ("security_check_fail", "Не удалось провести безопасную транзакцию."),
    )

    user = models.ForeignKey("auth.User", related_name="orders", on_delete=models.CASCADE, null=False,
                             blank=False, verbose_name="Позьзователь")
    delivery_type = models.CharField(max_length=50, null=False, blank=False, verbose_name="Тип доставки")
    delivery_price = models.DecimalField(max_digits=12, decimal_places=2, blank=False, verbose_name="Стоимость доставки")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, blank=False, verbose_name="Стоимость заказа")
    payment_type = models.ForeignKey("Payment", related_name="orders", on_delete=models.CASCADE, null=False,
                                     blank=False, verbose_name="Способ оплаты")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUSES, null=True, blank=True, verbose_name="Статус оплаты")
    city = models.CharField(max_length=50, verbose_name="Город")
    address = models.TextField(verbose_name="Адрес")
    status = models.CharField(max_length=8, choices=STATUSES, default="created", verbose_name="Статус заказа")
    comments = models.TextField(verbose_name="Комментарий")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ пользователя {self.user} # {self.pk}"


class OrderDetail(SoftDeleteModel):
    order_num = models.ForeignKey("Order", related_name="order_products", on_delete=models.CASCADE, null=False,
                                  blank=False, verbose_name="Заказ")
    good = models.ForeignKey("app_goods.Goods", related_name="orders_with_product", on_delete=models.CASCADE, null=False,
                             blank=False, verbose_name="Товар")
    amount = models.IntegerField(null=False, blank=False, verbose_name="Количество")
    price = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False, verbose_name="Цена")

    class Meta:
        verbose_name = "Товары в заказе"
        verbose_name_plural = "Товары в заказе"

    def __str__(self):
        return f"Заказ {self.order_num} продукт {self.good}"


class Payment(models.Model):
    PAYMENT_TYPE = (
        ("online", "Онлайн картой"),
        ("someone", "Онлайн со случайного чужого счета"),
    )
    type = models.CharField(max_length=50, choices=PAYMENT_TYPE, null=False, blank=False, verbose_name="Способ оплаты")
    slug = models.SlugField(unique=True, null=False, blank=False, verbose_name="Слаг")

    class Meta:
        verbose_name = "Способ оплаты"
        verbose_name_plural = "Способы оплаты"

    def __str__(self):
        return self.type
