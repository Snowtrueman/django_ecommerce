from django.db import models


class UserCart(models.Model):
    user = models.ForeignKey("auth.User", related_name="user_cart", on_delete=models.CASCADE,
                             verbose_name="Пользователь")
    good = models.ForeignKey("app_goods.Goods", related_name="goods_in_cart", on_delete=models.CASCADE,
                             verbose_name="Товар")
    amount = models.IntegerField(null=False, blank=False, verbose_name="Количество")

    class Meta:
        verbose_name = "Корзина пользователя"
        verbose_name_plural = "Корзина пользователя"
        ordering = ["pk"]

    def __str__(self):
        return f"{self.user} {self.good}"
