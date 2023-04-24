from app_users.models import Settings


class OrderDetails:
    def __init__(self, request, fullname=None, phone=None, email=None):
        self.fullname = fullname
        self.phone = phone
        self.email = email
        self.delivery_type = None
        self.delivery_price = 0
        self.city = None
        self.address = None
        self.payment_type = None
        self.step_1 = False
        self.step_2 = False
        self.step_3 = False
        self.session = request.session
        order_details = self.session.get("order_details")
        if not order_details:
            order_details = self.session["order_details"] = \
                {"fullname": self.fullname, "phone": self.phone, "email": self.email,
                 "delivery_type": self.delivery_type, "city": self.city, "address": self.address,
                 "payment_type": self.payment_type, "step_1": self.step_1, "step_2": self.step_2, "step_3": self.step_3}
        self.order_details = order_details

    def set_attribute(self, attr, value):
        try:
            self.order_details[attr] = value
            self.save()
        except KeyError:
            pass

    def step_completed(self, step):
        self.order_details[step] = True
        self.save()

    def save(self):
        self.session.modified = True
        self.session["order_details"] = self.order_details

    def clear(self):
        del self.session["order_details"]
        self.session.modified = True


def calculate_delivery_price(delivery_type, total_sum):
    result_price = 0
    settings = Settings.objects.first()
    ordinary_delivery_price = settings.ordinary_delivery_price
    express_delivery_price = settings.express_delivery_price
    delivery_sum_to_free = settings.delivery_sum_to_free

    if total_sum >= delivery_sum_to_free:
        if delivery_type == "express":
            result_price += express_delivery_price
            return result_price
        else:
            return result_price
    else:
        if delivery_type == "express":
            result_price = ordinary_delivery_price + express_delivery_price
            return result_price
        else:
            result_price = ordinary_delivery_price
            return result_price


