from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.urls import reverse_lazy
from app_orders.models import SoftDeleteModel


class Categories(SoftDeleteModel):
    title = models.CharField(max_length=50, blank=False, verbose_name="Название")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    sort_index = models.IntegerField(default=1, verbose_name="Индекс сортировки")
    icon = models.FileField(upload_to="category_pictures", null=True, verbose_name="Иконка")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True,
                               related_name="subcategories", verbose_name="Родительская категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    selected = models.BooleanField(default=False, verbose_name="Избранная категория")
    img = models.ImageField(upload_to="categories", null=True, blank=True, verbose_name="Картинка")

    class Meta:
        verbose_name = "Категория товаров"
        verbose_name_plural = "Категории товаров"
        ordering = ("sort_index",)

    def __str__(self):
        return self.title

    @staticmethod
    def get_name_by_slug(slug):
        return Categories.objects.values("title").filter(slug=slug).first()


@receiver(post_save, sender=Categories)
def clear_cache_actions(sender, instance, **kwargs):
    cache.delete("menu_categories")


@receiver(pre_save, sender=Categories)
def category_icon_and_img_pre_save_handler(sender, instance, **kwargs):
    try:
        category = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass
    else:
        if category.icon != instance.icon:
            if category.icon:
                storage, path = category.icon.storage, category.icon.path
                storage.delete(path)
        if category.img != instance.img:
            if category.img:
                storage, path = category.img.storage, category.img.path
                storage.delete(path)


@receiver(post_delete, sender=Categories)
def user_avatar_post_delete_handler(sender, instance, **kwargs):
    if instance.icon:
        storage, path = instance.icon.storage, instance.icon.path
        storage.delete(path)
    if instance.img:
        storage, path = instance.img.storage, instance.img.path
        storage.delete(path)


class Params(SoftDeleteModel):
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="Название характеристики")
    category = models.ForeignKey("Categories", on_delete=models.CASCADE, null=False, blank=False,
                                 related_name="params", verbose_name="Категория")
    main = models.BooleanField(default=True, verbose_name="Основной параметр")

    class Meta:
        verbose_name = "Параметр товаров"
        verbose_name_plural = "Параметры товаров"

    def __str__(self):
        return self.category.__str__() + " " + self.name


class ParamValues(SoftDeleteModel):
    good = models.ForeignKey("Goods", on_delete=models.CASCADE, null=False, blank=False,
                             related_name="params", verbose_name="Товар")
    param = models.ForeignKey("Params", on_delete=models.CASCADE, null=False, blank=False,
                              related_name="values", verbose_name="Характеристика")
    value = models.CharField(max_length=255, null=False, blank=False, verbose_name="Значение характеристики")

    class Meta:
        verbose_name = "Значение характиристики"
        verbose_name_plural = "Значения характеристик"
        unique_together = (("good", "param", "value"),)

    def __str__(self):
        return f"{self.param} {self.value}"


class Tags(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Goods(SoftDeleteModel):
    part_num = models.IntegerField(null=False, blank=False, verbose_name="Артикул")
    title = models.CharField(max_length=255, null=False, blank=False, verbose_name="Название")
    short_description = models.CharField(max_length=255, null=False, blank=False, verbose_name="Короткое Описание")
    description = models.TextField(null=False, blank=False, verbose_name="Полное описание")
    price = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False, verbose_name="Цена")
    amount = models.IntegerField(null=False, blank=False, verbose_name="Остаток")
    free_delivery = models.BooleanField(default=False, verbose_name="Бесплатная доставка")
    sort_index = models.IntegerField(default=1, null=False, blank=False, verbose_name="Индекс сортировки")
    limited = models.BooleanField(default=False, null=False, blank=False, verbose_name="Спецпредложение")
    is_published = models.BooleanField(default=True, null=False, blank=False, verbose_name="Опубликовано")
    date_published = models.DateField(auto_now=True, null=False, blank=False, verbose_name="Дата публикации")
    # purchases = models.IntegerField(default=0, null=False, blank=False, verbose_name="Количество покупок")
    category = models.ForeignKey("Categories", on_delete=models.CASCADE, null=False, blank=False,
                                 related_name="goods", verbose_name="Категория")
    tags = models.ManyToManyField("Tags", blank=True,
                                  related_name="goods_with_tag", verbose_name="Теги")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ("date_published",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy("product", kwargs={"category_slug": self.category.slug, "product_id": self.pk})


@receiver(post_save, sender=Goods)
def clear_cache_goods(sender, instance, **kwargs):
    cache.delete(f"product_{instance.pk}")


class ImageGallery(SoftDeleteModel):
    good = models.ForeignKey("Goods", related_name="images", on_delete=models.CASCADE, verbose_name="Товар")
    img = models.ImageField(upload_to="goods", null=True, blank=True, verbose_name="Картинка")
    main = models.BooleanField(default=False, verbose_name="Главное изображение")

    class Meta:
        verbose_name = "Галерея"
        verbose_name_plural = "Галерея"
        ordering = ("-main",)

    def __str__(self):
        return f"{self.pk} {self.good.__str__()}"


@receiver(pre_save, sender=ImageGallery)
def good_image_pre_save_handler(sender, instance, **kwargs):
    try:
        image = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass
    else:
        if image.img != instance.img:
            if image.img:
                storage, path = image.img.storage, image.img.path
                storage.delete(path)


@receiver(post_delete, sender=ImageGallery)
def good_image_post_delete_handler(sender, instance, **kwargs):
    if instance.img:
        storage, path = instance.img.storage, instance.img.path
        storage.delete(path)


class Reviews(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=False, blank=False,
                             related_name="user_reviews", verbose_name="Пользователь")
    good = models.ForeignKey("Goods", on_delete=models.CASCADE, null=False, blank=False,
                             related_name="reviews", verbose_name="Товар")
    text = models.TextField(null=False, blank=False, verbose_name="Текст")
    date_published = models.DateTimeField(auto_now=True, null=False, blank=False, verbose_name="Дата публикации")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ("date_published",)

    def __str__(self):
        return f"{self.date_published} {self.user} {self.good}"


@receiver(post_save, sender=Reviews)
def reviews_post_save_handler(sender, instance, **kwargs):
    try:
        good = Goods.objects.get(pk=instance.good.pk)
    except sender.DoesNotExist:
        pass
    else:
        cache.delete(f"product_{good.pk}")
