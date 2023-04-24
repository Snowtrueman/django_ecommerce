from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView, UpdateView, ListView
from app_orders.models import Order
from .forms import RegistrationForm, UpdateProfileForm, SettingsForm
from .models import UserProfile, Settings
from django.contrib.auth.views import PasswordResetView
from django.contrib import messages
from app_goods.utils import TitleMixin
from .utils import ProfilePagesMixin


class UserLogin(TitleMixin, LoginView):
    form_class = AuthenticationForm
    template_name = "app_users/auth/login.html"
    title = "Megano | Вход"
    redirect_authenticated_user = True


class UserLogout(LogoutView):
    next_page = reverse_lazy("main")


class UserRegister(TitleMixin, FormView):
    form_class = RegistrationForm
    template_name = "app_users/auth/register.html"
    success_url = reverse_lazy("main")
    title = "Megano | Регистрация"

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                name=form.cleaned_data.get("name"),
                surname=form.cleaned_data.get("surname"),
                email=form.cleaned_data.get("email"),
                phone=form.cleaned_data.get("phone"),
                city=form.cleaned_data.get("city"),
                slug=form.cleaned_data.get("username")
            )
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect("main")
        else:
            return render(request, "app_users/auth/register.html", context={"form": form})


class PasswordReset(TitleMixin, PasswordResetView):
    template_name = "app_users/auth/password_reset_form.html"
    email_template_name = "app_users/auth/reset_email.html"
    success_url = reverse_lazy("password-reset-done")
    from_email = "company@company.com"
    title = "Megano | Восстановление пароля"


class PasswordResetDone(TitleMixin, PasswordResetDoneView):
    template_name = "app_users/auth/password_reset_done.html"
    title = "Megano | Восстановление пароля"


class PasswordResetConfirm(TitleMixin, PasswordResetConfirmView):
    template_name = "app_users/auth/password_reset.html"
    success_url = reverse_lazy("password-reset-success")
    title = "Megano | Восстановление пароля"


class PasswordResetComplete(TitleMixin, PasswordResetCompleteView):
    template_name = "app_users/auth/password_reset_success.html"
    title = "Megano | Восстановление пароля"


class Account(UserPassesTestMixin, TitleMixin, ProfilePagesMixin, DetailView):
    model = UserProfile
    template_name = "app_users/account.html"
    context_object_name = "user_account"
    slug_url_kwarg = "user_slug"
    title = "Megano | Личный кабинет"
    account_title = "Личный кабинет"
    active = True

    def test_func(self, **kwargs):
        current_object = UserProfile.objects.filter(slug=self.kwargs.get("user_slug")).values("user_id").first()
        if not current_object:
            return False
        return self.request.user.is_superuser or current_object.get("user_id") == self.request.user.id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["last_order"] = Order.objects.filter(user=self.request.user).select_related("payment_type") \
            .order_by("-date").first()
        return context


class Profile(UserPassesTestMixin, TitleMixin, ProfilePagesMixin, DetailView):
    model = UserProfile
    form_class = UpdateProfileForm
    template_name = "app_users/profile.html"
    context_object_name = "user_account"
    slug_url_kwarg = "user_slug"
    title = "Megano | Профиль пользователя"
    account_title = "Профиль пользователя"
    active = True

    def test_func(self, **kwargs):
        current_object = UserProfile.objects.filter(slug=self.kwargs.get("user_slug")).values("user_id").first()
        if not current_object:
            return False
        return self.request.user.is_superuser or current_object.get("user_id") == self.request.user.id

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        form = UpdateProfileForm(request.POST)
        user_profile = UserProfile.objects.get(user__username=self.kwargs["user_slug"])
        user = User.objects.get(username=self.kwargs["user_slug"])
        if form.is_valid():
            name, surname = form.cleaned_data.get("full_name").split()
            email = form.cleaned_data.get("email")
            phone = form.cleaned_data.get("phone")
            if request.FILES.get("avatar"):
                avatar = request.FILES.get("avatar")
                user_profile.avatar = avatar
            password1 = form.cleaned_data.get("password1")
            password2 = form.cleaned_data.get("password2")
            user_profile.name = name
            user_profile.surname = surname
            if "email" in form.cleaned_data:
                user_profile.email = email
                user.email = email
                user.save()
            user_profile.phone = phone
            if password1 != "" or password2 != "":
                if password1 != password2:
                    messages.error(request, "Введённые пароли не совпадают!")
                    return render(request, "app_users/profile.html", context=context)
                user.set_password(password1)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Пароль успешно изменён!")
            user_profile.save()
            return redirect("profile", user_slug=self.kwargs["user_slug"])
        else:
            context["form"] = form
            return render(request, "app_users/profile.html", context=context)


class SiteSettings(UserPassesTestMixin, TitleMixin, ProfilePagesMixin, UpdateView):
    form_class = SettingsForm
    template_name = "app_users/settings.html"
    context_object_name = "site_settings"
    title = "Megano | Настройки сайта"
    account_title = "Настройки сайта"
    active = True
    success_url = reverse_lazy("settings")

    def test_func(self, **kwargs):
        return self.request.user.is_superuser

    def get_object(self, queryset=None):
        return Settings.objects.first()

    def form_valid(self, form):
        response = super(SiteSettings, self).form_valid(form)
        messages.success(self.request, "Настройки успешно изменены!")
        return response


class HistoryOrder(LoginRequiredMixin, TitleMixin, ProfilePagesMixin, ListView):
    model = Order
    template_name = "app_users/orders_history.html"
    context_object_name = "orders"
    title = "Megano | История заказов"
    account_title = "История заказов"
    active = True

    def test_func(self, **kwargs):
        return self.request.user.is_superuser or self.get == self.request.user.pk

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("payment_type")
