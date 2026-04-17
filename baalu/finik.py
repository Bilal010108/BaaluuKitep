import os
import time
import json
import base64
import requests
from urllib.parse import urljoin

from authorizer import Signer
from django.core.mail import send_mail
from django.utils import timezone

from .models import Payment



BASE_URL = "https://api.acquiring.averspay.kg"
HOST = "api.acquiring.averspay.kg"
API_KEY     = 'nNVdS0nN3z7sam6VxFroGa3AenwEwejx64WsBwrI'
PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDUNDz5+bWa8oEc\n4ArWslynxDiTIt3CsbwXjmtdxY0+2y0hvDc2C6hLZY4Nvzu1uWtSMSMsaLDl4mjH\n0UXxs90HX3glVflE+KIkajUnBVSYeuWa69zDciwXdKVsXjBwSaxOg3js3bHUs5SQ\nqDvgmbIJyxveIqQvxPYUH4etF5KEWppNS4hkMkDKjg4V4YeHL1r6qYr4vefZW3r6\n6wttvkSxYJlIEDrtPEYlvcnCj+R5F8TwJb0zZz0X6lXyPJdgi5ctqV+C0SjSOIde\niI4VIGuRLwv0l+JhM/RGpPveNPnTHnOXIr32kKsPStFsM2U4zU5DwAfstnLLKDv3\nv1ItS/udAgMBAAECggEAC43BkSm1p9dSzM/s/yYMcez22JoCIX7cWxr7wQoHx/eW\nhDrzdZuaYOqJWrnCBkGvdHTs8ZbMpOOYKWL9UCznGKbry3qcHRN9foaS2MpLQhcU\n58O2TCTr/iXxeM5DDGYSfd7eJ2VlsItLiDnEstSjczGOFaDkuB4c+NkDodrB9TdB\nKvd30AdxrM9SjFkhpIyE7tmV7Xj9wRi41wCJNWTcYYbeXF/AjiFvFFZtkjGrxWQ6\nC6BuH+aem+1+5xxZTQmUkEtBvdW5UgvauaoaFgn3x6ltWlny6TAL4fI8WOYSSUj3\njElgHjO9rfDLTqfU6b+aRF5rue+iZUAsk+pBdBtmcQKBgQD+sXfp+PD7UTg2uv1Z\nsZw9Z330w2X5J+JX6stv4X0wTHQbZF+r0DBIy+HTR7O/h/Ft9PCnNeFZPqGySyNs\nlBXM7PT9nmTB+8cOEuYjGNXSjXOZr4+skKPfyAWiH6DIkNtX7J32ii7IyioeMPgw\nq0yKZrjF0HLEjZFSX3Hx6hI9DQKBgQDVSvYpULWSSx1RN7lUpxdJdKRUZas18lA6\nxrPZ5fcFMU3bMVy7Po1PkWNwj68lPg8wYCuv9voPgGK2XsfHtexSUvDAlmwjs7BR\n44dRDtVT04X/Atg7Cs3Pg3BRwNg6ap4pukWdiY5tZ3ocbe0gBzu15LED6zOaqaqn\ngy+Fpqe00QKBgQDlHyf+HwpDPEyyx8MVBnfEsa6ZG5NH8n5nkvzSuGqToaOt5L1A\nZniZdHjCRjXI7vXdckVwV0NTsslqCLhkfE+kW+MFqZGBBQyMd6n7FuN8l+3P6yT4\nG+KgdWPD9moBJHd+gImWebcewOfk4y7TMbcYptJAeoZUlfqOvPhXpbgknQKBgEg3\nCiMw5Vjzv6hY8pG7xQGk0WKVzaMFOK69yfTzjHAgolidXOU0p4mSExXwP/+fBGt/\nlCsOttl6wXE3o/J1IN86n7LE+zYXR5JiM9V47TdlfY+6udU7sjUZLnUvksYshQJh\nw+IzyZo3F7v6Z/eZG1lZZamK/7zUxyfSHcvlghCRAoGAFEFWcSAMQW9zhb6AcRS+\nIvm4vMqP+YuPlRkdMPo7h6DJVASs1eOTvFQHGcwMRXr1V0nGk3K6uAv5Zgrta4uz\nPuOWf+rL1UFviFWvJOLIDlcBXIJXv1/iVOpRnDo6DlpcHDFK7R3t86pbNhEHoE+K\nRYXabHAiDIPDZ4hsBdR+ER0=\n-----END PRIVATE KEY-----\n"
ACCOUNT_ID = '548e4c5c-814a-402e-93ea-de4350c8b6a3'
FINIK_MCC = 5999


# Публичный ключ Finik для верификации входящих webhook-ов
# Production ключ — замени на Beta ключ если используешь beta.api.*
FINIK_PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuF/PUmhMPPidcMxhZBPb
BSGJoSphmCI+h6ru8fG8guAlcPMVlhs+ThTjw2LHABvciwtpj51ebJ4EqhlySPyT
hqSfXI6Jp5dPGJNDguxfocohaz98wvT+WAF86DEglZ8dEsfoumojFUy5sTOBdHEu
g94B4BbrJvjmBa1YIx9Azse4HFlWhzZoYPgyQpArhokeHOHIN2QFzJqeriANO+wV
aUMta2AhRVZHbfyJ36XPhGO6A5FYQWgjzkI65cxZs5LaNFmRx6pjnhjIeVKKgF99
4OoYCzhuR9QmWkPl7tL4Kd68qa/xHLz0Psnuhm0CStWOYUu3J7ZpzRK8GoEXRcr8
tQIDAQAB
-----END PUBLIC KEY-----"""


# ─── Создание QR-платежа ───────────────────────────────────────────────────────

def create_finik_payment(order):
    """
    Создаёт FINIK QR-платёж через официальный пакет authorizer.
    Возвращает (payment_url, payment_id).
    """
    timestamp = str(int(time.time() * 1000))
    path = "/v1/payment"

    body = {
        "Amount": int(order.total_price),
        "CardType": "FINIK_QR",
        "PaymentId": str(order.id),
        "RedirectUrl": "https://baaluukitep.kg/",
        "Data": {
            "accountId": ACCOUNT_ID,
            "merchantCategoryCode": FINIK_MCC,
            "name_en": "Baaluu Books",
            "description": f"Заказ №{order.id} Книги: {', '.join(f'{item.books.books_name} x{item.quantity}' for item in order.items.all())}",
            "webhookUrl": 'https://api.baaluukitep.com.kg/ru/lpayment/webhook/,'
        }

    }

    # Официальный Signer от Finik — строит canonical string правильно
    request_data = {
        "http_method": "POST",
        "path": path,
        "headers": {
            "Host": HOST,
            "x-api-key": API_KEY,
            "x-api-timestamp": timestamp,
        },
        "query_string_parameters": None,
        "body": body,
    }

    signature = Signer(**request_data).sign(PRIVATE_KEY)

    resp = requests.post(
        urljoin(BASE_URL, path),
        headers={
            "content-type": "application/json",
            "x-api-key": API_KEY,
            "x-api-timestamp": timestamp,
            "signature": signature,
        },
        data=json.dumps(body, separators=(",", ":")),
        allow_redirects=False,
        timeout=10,
    )

    if resp.status_code == 302:
        payment_url = resp.headers.get("Location")
        return payment_url, str(order.id)

    raise Exception(f"Finik error {resp.status_code}: {resp.text}")


# ─── Проверка подписи входящего webhook ───────────────────────────────────────

def verify_finik_webhook_signature(request):
    """
    Проверяет RSA-SHA256 подпись входящего webhook от Finik.
    Возвращает (True, "OK") или (False, "причина ошибки").
    """
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.backends import default_backend

    signature_b64 = request.headers.get("signature", "")
    timestamp     = request.headers.get("x-api-timestamp", "")

    # Проверка временной метки ±5 минут
    now_ms = int(time.time() * 1000)
    try:
        if abs(now_ms - int(timestamp)) > 5 * 60 * 1000:
            return False, "Timestamp expired"
    except ValueError:
        return False, "Invalid timestamp"

    # Парсим тело
    try:
        body_dict = json.loads(request.body)
    except json.JSONDecodeError:
        return False, "Bad JSON"

    # Строим canonical string (по той же схеме что при отправке)
    sorted_body = json.dumps(body_dict, sort_keys=True, separators=(",", ":"))
    host = request.headers.get("Host", "")

    xapi_headers = sorted([
        (k.lower(), v)
        for k, v in request.headers.items()
        if k.lower().startswith("x-api-")
    ])
    headers_str = f"host:{host}&" + "&".join(f"{k}:{v}" for k, v in xapi_headers)
    canonical = f"post\n{request.path}\n{headers_str}\n{sorted_body}"

    # Верифицируем через публичный ключ Finik
    try:
        public_key = serialization.load_pem_public_key(
            FINIK_PUBLIC_KEY_PEM.strip().encode(),
            backend=default_backend()
        )
        public_key.verify(
            base64.b64decode(signature_b64),
            canonical.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True, "OK"
    except Exception as e:
        return False, str(e)


# ─── Обработка успешной оплаты ────────────────────────────────────────────────

def handle_payment_success(payment):
    """
    После успешной оплаты меняет статус заказа и отправляет email покупателю.
    """
    order = payment.order
    order.status = 'Отправлен'
    order.save(update_fields=['status'])

    send_mail(
        subject=f'✅ Заказ #{order.id} оплачен',
        message=(
            f'Привет, {order.user.username}!\n\n'
            f'Ваш заказ #{order.id} на сумму {order.total_price} сом успешно оплачен.\n'
            f'Адрес доставки: {order.address}\n\n'
            f'Спасибо за покупку в Baaluu Books!'
        ),
        from_email=os.getenv('EMAIL_HOST_USER'),
        recipient_list=[order.user.email],
        fail_silently=True,
    )