from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from app_orders.models import SoftDeleteModel

User._meta.get_field("email")._unique = True


class UserProfile(SoftDeleteModel):
    ROLES = (
        ("Admin", "Admin"),
        ("User", "User"),
        ("Guest", "Guest"),
    )
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE, verbose_name="User")
    role = models.CharField(max_length=5, choices=ROLES, default="User", verbose_name="Роль пользователя")
    name = models.CharField(max_length=50, blank=False, verbose_name="Имя")
    surname = models.CharField(max_length=50, blank=True, verbose_name="Фамилия")
    email = models.EmailField(blank=False, unique=True, verbose_name="E-mail")
    phone = models.CharField(max_length=15, blank=False, verbose_name="Телефон")
    city = models.CharField(max_length=50, null=True, blank=True, verbose_name="Город")
    orders = models.CharField(max_length=50, null=True, blank=True, verbose_name="Заказы")
    avatar = models.ImageField(upload_to="user_avatars", null=True, blank=True, verbose_name="Аватар")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    class Meta:
        verbose_name ="Профиль пользователя"
        verbose_name_plural = "Профили пользователя"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("account", kwargs={"user_slug": self.slug})


@receiver(pre_save, sender=UserProfile)
def user_avatar_pre_save_handler(sender, instance, **kwargs):
    try:
        user = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass
    else:
        if user.avatar != instance.avatar:
            if user.avatar:
                storage, path = user.avatar.storage, user.avatar.path
                storage.delete(path)


@receiver(post_delete, sender=UserProfile)
def user_avatar_post_delete_handler(sender, instance, **kwargs):
    if instance.avatar:
        storage, path = instance.avatar.storage, instance.avatar.path
        storage.delete(path)


class Settings(models.Model):
    general_phone = models.CharField(max_length=16, verbose_name="Общий номер телефона")
    general_email = models.CharField(max_length=50, verbose_name="Общий email")
    general_address = models.TextField(verbose_name="Общий адрес")
    facebook_url = models.TextField(max_length=50, verbose_name="Страница в Facebook")
    twitter_url = models.TextField(max_length=50, verbose_name="Страница в Twitter")
    linkedin_url = models.TextField(max_length=50, verbose_name="Страница в LinkedIn")
    pinterest_url = models.TextField(max_length=50, verbose_name="Страница в Pinterest")
    product_cache_time = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(31536000)],
                                             verbose_name="Время кеширования карточки товара (с)")
    ordinary_delivery_price = models.IntegerField(verbose_name="Стоимость обычной доставки")
    express_delivery_price = models.IntegerField(verbose_name="Стоимость экспресс-доставки")
    delivery_sum_to_free = models.IntegerField(verbose_name="Порог бесплатной доставки")


    class Meta:
        verbose_name = "Настройки"
        verbose_name_plural = "Настройки"

    def __str__(self):
        return "Настройки сайта"

    def save(self, *args, **kwargs):
        if not Settings.objects.filter(pk=self.pk).exists() and Settings.objects.exists():
            return
        return super(Settings, self).save(*args, **kwargs)


@receiver(post_save, sender=Settings)
def clear_cache_actions(sender, instance, **kwargs):
    cache.delete("settings")
