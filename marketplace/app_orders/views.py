from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import F
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.views.generic import TemplateView, FormView, DetailView
from app_cart.cart import Cart
from app_users.models import UserProfile
from .forms import OrderParamForm, OrderDeliveryForm, OrderPaymentForm
from .models import Order, OrderDetail, Payment
from app_goods.models import Goods
from .utils import OrderDetails, calculate_delivery_price
from django.db import transaction
from .tasks import perform_payment
from app_goods.utils import TitleMixin


class CheckOutView(UserPassesTestMixin, TitleMixin, FormView):
    template_name = "app_orders/order.html"
    form_class = OrderParamForm
    permission_denied_message = "Для оформления заказа необходимо добавить товары в корзину."
    raise_exception = False
    title = "Megano | Оформление заказа"

    def test_func(self, **kwargs):
        cart = Cart(self.request)
        return len(cart)

    def get(self, request, **kwargs):
        current_order = OrderDetails(self.request)
        current_order.clear()
        return super().get(self, request, **kwargs)

    def post(self, request, **kwargs):
        form = OrderParamForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("password1") and form.cleaned_data.get("password2"):

                user = User.objects.filter(email=form.cleaned_data.get("email"))
                if user and not request.user.is_authenticated:
                    form.add_error("email", "Пользователь с таким email уже существует")
                    return render(request, "app_orders/order.html", context={"form": form})
                username, *_ = form.cleaned_data.get("email").split("@")
                user = User.objects.create(
                    username=username,
                    password=make_password(form.cleaned_data.get("password1")),
                    email=form.cleaned_data.get("email")
                )
                UserProfile.objects.create(
                    user=user,
                    name=form.cleaned_data.get("fullname"),
                    email=form.cleaned_data.get("email"),
                    phone=form.cleaned_data.get("phone"),
                    slug=username
                )
                username = form.cleaned_data.get("email")
                password = form.cleaned_data.get("password1")
                user = authenticate(username=username, password=password)
                login(request, user)
            if request.user.is_authenticated:
                current_order = OrderDetails(self.request)
                current_order.clear()
                order_details = OrderDetails(
                    request=request, fullname=form.cleaned_data.get("fullname"), phone=form.cleaned_data.get("phone"),
                    email=form.cleaned_data.get("email")
                )
                order_details.step_completed("step_1")
                return redirect(reverse_lazy("checkout_delivery"))
            else:
                form.add_error("password1", "Вы должны войти или зарегистрироваться")
                form.add_error("password2", "Вы должны войти или зарегистрироваться")
                return render(request, "app_orders/order.html", context={"form": form})
        else:
            return render(request, "app_orders/order.html", context={"form": form})


class CheckOutDeliveryView(UserPassesTestMixin, TitleMixin, FormView):
    template_name = "app_orders/delivery.html"
    form_class = OrderDeliveryForm
    title = "Megano | Оформление заказа"
    permission_denied_message = "Для выбора способа доставки необходимо заполнить данные о пользователе. " \
                                "Вернитесь на первый этап."
    raise_exception = False

    def test_func(self, **kwargs):
        cart = Cart(self.request)
        current_order = OrderDetails(self.request)
        return len(cart) and current_order.order_details["step_1"] is True

    def post(self, request, **kwargs):
        cart = Cart(self.request)
        form = OrderDeliveryForm(request.POST)
        if form.is_valid():
            current_order = OrderDetails(self.request)
            current_order.set_attribute("delivery_type", form.cleaned_data.get("delivery"))
            current_order.set_attribute("city", form.cleaned_data.get("city"))
            current_order.set_attribute("address", form.cleaned_data.get("address"))
            current_order.set_attribute("delivery_price",
                                        calculate_delivery_price(form.cleaned_data.get("delivery"), cart.get_total_price()))
            current_order.step_completed("step_2")

            return redirect(reverse_lazy("checkout_payment"))
        else:
            return render(request, "app_orders/delivery.html", context={"form": form})


class CheckOutPaymentView(UserPassesTestMixin, TitleMixin, FormView):
    template_name = "app_orders/payment.html"
    title = "Megano | Оформление заказа"
    form_class = OrderPaymentForm
    permission_denied_message = "Для выбора способа оплаты необходимо заполнить данные о пользователе и выбрать " \
                                "способ доставки. Вернитесь на второй этап."
    raise_exception = False

    def test_func(self, **kwargs):
        cart = Cart(self.request)
        current_order = OrderDetails(self.request)
        return len(cart) and current_order.order_details["step_2"] is True

    def post(self, request, **kwargs):
        form = OrderPaymentForm(request.POST)
        if form.is_valid():
            current_order = OrderDetails(self.request)
            current_order.set_attribute("payment_type", form.cleaned_data.get("payment"))

            current_order.step_completed("step_3")

            return redirect(reverse_lazy("checkout_summary"))
        else:
            return render(request, "app_orders/payment.html", context={"form": form})


class CheckOutSummaryView(UserPassesTestMixin, TitleMixin, TemplateView):
    template_name = "app_orders/summary.html"
    title = "Megano | Оформление заказа"
    permission_denied_message = "Для просмотра предварительный информации о заказе необходимо корректно завершить " \
                                "все этапы его оформления."
    raise_exception = False

    def test_func(self, **kwargs):
        cart = Cart(self.request)
        current_order = OrderDetails(self.request)
        return len(cart) and current_order.order_details["step_3"] is True

    def post(self, request, **kwargs):
        flag = False
        cart = Cart(request)
        context = self.get_context_data()
        for product in cart:
            if product["quantity"] > product["good"].amount:
                context[f"error_{product['good'].pk}"] = f"К сожалению, товар в данном количестве отсутствует. " \
                                                         f"На данный момент доступно {product['good'].amount} шт. " \
                                                         f"Измените количество в корзине."
                flag = True
        if flag:
            return render(request, "app_orders/summary.html", context=context)
        with transaction.atomic():
            current_order = OrderDetails(self.request)
            payment_type = current_order.order_details.get("payment_type")
            order = Order.objects.create(
                user=request.user,
                delivery_type=current_order.order_details.get("delivery_type"),
                payment_type=Payment.objects.filter(slug=current_order.order_details.get("payment_type")).first(),
                delivery_price=current_order.order_details.get("delivery_price"),
                total_price=cart.get_total_price(),
                city=current_order.order_details.get("city"),
                address=current_order.order_details.get("address"),
                status="created",
                comments="")
            current_order.clear()
            for product in cart:
                Goods.objects.select_for_update().filter(pk=product["good"].pk)\
                    .update(amount=F("amount") - product["quantity"])
                OrderDetail.objects.create(
                    order_num=order,
                    good=product["good"],
                    amount=product["quantity"],
                    price=product["price"])
            cart.clear()
            redirect_url = reverse_lazy("payment", kwargs={"payment_type": payment_type})
            params = f"order_number={order.pk}"
            return redirect(f"{redirect_url}?{params}")


class PaymentView(UserPassesTestMixin, TitleMixin, LoginRequiredMixin, TemplateView):
    title = "Megano | Оплата заказа"
    permission_denied_message = "У вас нет права на просмотр указанного заказа или он уже успешно оплачен."
    raise_exception = False

    def test_func(self, **kwargs):
        order_number = self.request.GET.get("order_number")
        order = Order.objects.filter(pk=order_number).first()
        if order:
            if order.status == "created" and order.user == self.request.user:
                return True
        else:
            return False

    def get_template_names(self):
        if self.kwargs.get("payment_type") == "online":
            return "app_orders/payment_card.html"
        elif self.kwargs.get("payment_type") == "someone":
            return "app_orders/payment_account.html"

    def post(self, request, **kwargs):
        order_number = request.GET.get("order_number")
        card_number = request.POST.get("card_number")
        if card_number:
            perform_payment.delay(order_number, card_number)
            return redirect(reverse_lazy("order_detail", kwargs={"order_id": order_number}))
        else:
            ...


class OrderDetailView(UserPassesTestMixin, TitleMixin, DetailView):
    model = Order
    pk_url_kwarg = "order_id"
    template_name = "app_orders/order_detail.html"
    context_object_name = "order"

    def get_title(self, context):
        return f"Megano | Заказ пользователя №{self.object.pk}"

    def test_func(self, **kwargs):
        current_object = Order.objects.filter(pk=self.kwargs.get("order_id")).values("user_id").first()
        if not current_object:
            return False
        return self.request.user.is_superuser or current_object.get("user_id") == self.request.user.id

    def get_queryset(self):
        return Order.objects.filter(pk=self.kwargs.get("order_id")).select_related("user")\
            .select_related("payment_type")\
            .prefetch_related("user__profile").prefetch_related("order_products")\
            .prefetch_related("order_products__good").prefetch_related("order_products__good__images")
