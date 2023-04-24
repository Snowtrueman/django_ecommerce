import requests
import json
from django.urls import reverse_lazy
from marketplace.celery import app
from .models import Order
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@app.task(bind=True, max_retries=3)
def perform_payment(self, order_number, card_number):
    data = {"card_number": card_number}
    url = reverse_lazy("perform_payment")
    domain = "http://web:8000"
    do_payment = requests.post(f"{domain}{url}", data=data, timeout=60)
    if do_payment.status_code in [100, 200, 400]:
        response = json.loads(do_payment.text)
        order = Order.objects.get(pk=order_number)
        order.payment_status = response["status"]
        if do_payment.status_code == 200:
            order.status = "paid"
        order.save()
    else:
        self.retry(countdown=5 ** self.request.retries)
