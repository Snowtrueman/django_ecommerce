from django.urls import path
from .views import *

urlpatterns = [
    path("login/", UserLogin.as_view(), name="login"),
    path("logout/", UserLogout.as_view(), name="logout"),
    path("register/", UserRegister.as_view(), name="register"),
    path("password-reset/", PasswordReset.as_view(), name="password-reset"),
    path("password-reset-done/", PasswordResetDone.as_view(), name="password-reset-done"),
    path("reset/<uidb64>/<token>/", PasswordResetConfirm.as_view(), name="password_reset_confirm"),
    path("password-reset-success/", PasswordResetComplete.as_view(), name="password-reset-success"),
    path("account/<slug:user_slug>/", Account.as_view(), name="account"),
    path("profile/<slug:user_slug>/", Profile.as_view(), name="profile"),
    path("settings/", SiteSettings.as_view(), name="settings"),
    path("orders/", HistoryOrder.as_view(), name="orders_history"),
]
