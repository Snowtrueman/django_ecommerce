from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView
from app_cart.cart import Cart
from app_goods.models import Goods
from app_goods.utils import TitleMixin
from django.contrib import messages


class CartView(TitleMixin, TemplateView):
    template_name = "app_cart/cart.html"
    title = "Megano | Корзина"


class CartDeleteView(TitleMixin, TemplateView):
    template_name = "app_cart/cart.html"
    title = "Megano | Корзина"

    def get(self, request, *args, **kwargs):
        cart = Cart(self.request)
        cart.remove(self.kwargs["product_id"])
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


class CartEditView(TitleMixin, TemplateView):
    template_name = "app_cart/cart.html"
    title = "Megano | Корзина"

    def get(self, request, *args, **kwargs):
        cart = Cart(self.request)
        product = Goods.objects.filter(pk=self.kwargs["product_id"]).first()
        match self.kwargs["action"]:
            case "decrease":
                cart.sub(product)
            case "increase":
                cart.add(product=product)
            case "add":
                quantity = self.kwargs.get("quantity", 1)
                cart.add(product=product, quantity=quantity)
                messages.success(request, "successfully_added")
                return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)
