from django.urls import path
from .views import PaymentAPIView

urlpatterns = [
    path("api/v1/payment/", PaymentAPIView.as_view(), name="perform_payment"),
]
