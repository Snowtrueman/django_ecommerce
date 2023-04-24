from django.urls import path
from .views import CartView, CartDeleteView, CartEditView

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/delete/<int:product_id>/", CartDeleteView.as_view(), name="cart-delete"),
    path("cart/edit/<int:product_id>/<str:action>", CartEditView.as_view(), name="cart-edit"),
    path("cart/edit/<int:product_id>/<str:action>/<int:quantity>", CartEditView.as_view(), name="cart-add_amount"),
]