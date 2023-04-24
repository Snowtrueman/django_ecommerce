from rest_framework.response import Response
from rest_framework.views import APIView
import random
import time


class PaymentAPIView(APIView):
    ERRORS = {
        "invalid_number": "Указанный номер карты недействителен.",
        "card_expired": "Срок действия карты истёк.",
        "insufficient funds": "На карте недостаточно средств.",
        "processing_error": "Ошибка на стороне платёжной системы.",
        "security_check_fail": "Не удалось провести безопасную транзакцию.",
    }

    def post(self, request):
        time.sleep(5)
        card_number = request.data["card_number"].replace(" ", "")
        length = len(card_number)
        last_digit = card_number[-1]
        if card_number.isdigit():
            card_number = int(card_number)
        else:
            return Response({"status": "invalid_number", "description": self.ERRORS["invalid_number"],
                             "card_number": card_number}, status=400)
        if length == 8 and last_digit != "0" and card_number % 2 == 0:
            return Response({"status": "OK", "description": "Оплата прошла успешно.",
                             "card_number": card_number}, status=200)
        else:
            status = random.choice(list(self.ERRORS.keys()))
            description = self.ERRORS[status]
            return Response({"status": status, "description": description,
                             "card_number": card_number}, status=400)
