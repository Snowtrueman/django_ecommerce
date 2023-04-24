from django.urls import path
from .views import *

urlpatterns = [
    path("checkout/", CheckOutView.as_view(), name="checkout"),
    path("checkout/delivery/", CheckOutDeliveryView.as_view(), name="checkout_delivery"),
    path("checkout/payment/", CheckOutPaymentView.as_view(), name="checkout_payment"),
    path("checkout/summary/", CheckOutSummaryView.as_view(), name="checkout_summary"),
    path("payment/<str:payment_type>/", PaymentView.as_view(), name="payment"),
    path("orders/<int:order_id>/", OrderDetailView.as_view(), name="order_detail"),
]
