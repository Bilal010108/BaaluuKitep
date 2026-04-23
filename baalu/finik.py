import json
import time
import requests
from urllib.parse import urljoin
from uuid import uuid4
import unidecode
from authorizer import Signer
from django.core.mail import send_mail
import os




BASE_URL = "https://api.acquiring.averspay.kg"
HOST = "api.acquiring.averspay.kg"
API_KEY     = 'nNVdS0nN3z7sam6VxFroGa3AenwEwejx64WsBwrI'
PRIVATE_KEY_PEM  = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDUNDz5+bWa8oEc\n4ArWslynxDiTIt3CsbwXjmtdxY0+2y0hvDc2C6hLZY4Nvzu1uWtSMSMsaLDl4mjH\n0UXxs90HX3glVflE+KIkajUnBVSYeuWa69zDciwXdKVsXjBwSaxOg3js3bHUs5SQ\nqDvgmbIJyxveIqQvxPYUH4etF5KEWppNS4hkMkDKjg4V4YeHL1r6qYr4vefZW3r6\n6wttvkSxYJlIEDrtPEYlvcnCj+R5F8TwJb0zZz0X6lXyPJdgi5ctqV+C0SjSOIde\niI4VIGuRLwv0l+JhM/RGpPveNPnTHnOXIr32kKsPStFsM2U4zU5DwAfstnLLKDv3\nv1ItS/udAgMBAAECggEAC43BkSm1p9dSzM/s/yYMcez22JoCIX7cWxr7wQoHx/eW\nhDrzdZuaYOqJWrnCBkGvdHTs8ZbMpOOYKWL9UCznGKbry3qcHRN9foaS2MpLQhcU\n58O2TCTr/iXxeM5DDGYSfd7eJ2VlsItLiDnEstSjczGOFaDkuB4c+NkDodrB9TdB\nKvd30AdxrM9SjFkhpIyE7tmV7Xj9wRi41wCJNWTcYYbeXF/AjiFvFFZtkjGrxWQ6\nC6BuH+aem+1+5xxZTQmUkEtBvdW5UgvauaoaFgn3x6ltWlny6TAL4fI8WOYSSUj3\njElgHjO9rfDLTqfU6b+aRF5rue+iZUAsk+pBdBtmcQKBgQD+sXfp+PD7UTg2uv1Z\nsZw9Z330w2X5J+JX6stv4X0wTHQbZF+r0DBIy+HTR7O/h/Ft9PCnNeFZPqGySyNs\nlBXM7PT9nmTB+8cOEuYjGNXSjXOZr4+skKPfyAWiH6DIkNtX7J32ii7IyioeMPgw\nq0yKZrjF0HLEjZFSX3Hx6hI9DQKBgQDVSvYpULWSSx1RN7lUpxdJdKRUZas18lA6\nxrPZ5fcFMU3bMVy7Po1PkWNwj68lPg8wYCuv9voPgGK2XsfHtexSUvDAlmwjs7BR\n44dRDtVT04X/Atg7Cs3Pg3BRwNg6ap4pukWdiY5tZ3ocbe0gBzu15LED6zOaqaqn\ngy+Fpqe00QKBgQDlHyf+HwpDPEyyx8MVBnfEsa6ZG5NH8n5nkvzSuGqToaOt5L1A\nZniZdHjCRjXI7vXdckVwV0NTsslqCLhkfE+kW+MFqZGBBQyMd6n7FuN8l+3P6yT4\nG+KgdWPD9moBJHd+gImWebcewOfk4y7TMbcYptJAeoZUlfqOvPhXpbgknQKBgEg3\nCiMw5Vjzv6hY8pG7xQGk0WKVzaMFOK69yfTzjHAgolidXOU0p4mSExXwP/+fBGt/\nlCsOttl6wXE3o/J1IN86n7LE+zYXR5JiM9V47TdlfY+6udU7sjUZLnUvksYshQJh\nw+IzyZo3F7v6Z/eZG1lZZamK/7zUxyfSHcvlghCRAoGAFEFWcSAMQW9zhb6AcRS+\nIvm4vMqP+YuPlRkdMPo7h6DJVASs1eOTvFQHGcwMRXr1V0nGk3K6uAv5Zgrta4uz\nPuOWf+rL1UFviFWvJOLIDlcBXIJXv1/iVOpRnDo6DlpcHDFK7R3t86pbNhEHoE+K\nRYXabHAiDIPDZ4hsBdR+ER0=\n-----END PRIVATE KEY-----\n"
ACCOUNT_ID = '548e4c5c-814a-402e-93ea-de4350c8b6a3'
FINIK_MCC = 5999
WEBHOOK_URL = 'https://api.baaluukitep.com.kg/ru/payment/webhook/'
REDIRECT_URL = 'https://baaluukitep.kg/'

FINIK_PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuF/PUmhMPPidcMxhZBPb
BSGJoSphmCI+h6ru8fG8guAlcPMVlhs+ThTjw2LHABvciwtpj51ebJ4EqhlySPyT
hqSfXI6Jp5dPGJNDguxfocohaz98wvT+WAF86DEglZ8dEsfoumojFUy5sTOBdHEu
g94B4BbrJvjmBa1YIx9Azse4HFlWhzZoYPgyQpArhokeHOHIN2QFzJqeriANO+wV
aUMta2AhRVZHbfyJ36XPhGO6A5FYQWgjzkI65cxZs5LaNFmRx6pjnhjIeVKKgF99
4OoYCzhuR9QmWkPl7tL4Kd68qa/xHLz0Psnuhm0CStWOYUu3J7ZpzRK8GoEXRcr8
tQIDAQAB
-----END PUBLIC KEY-----"""

class FinikClient:

    def __init__(self):
        if not API_KEY or not PRIVATE_KEY_PEM:
            raise ValueError("API_KEY и PRIVATE_KEY_PEM должны быть заданы")

    def create_payment(self, user, amount: int, order) -> dict:
        timestamp = str(int(time.time() * 1000))
        payment_id = str(uuid4())

        # Описание из товаров заказа
        description_original = "; ".join([
            f"{item.books.books_name} x{item.quantity}"
            for item in order.items.select_related('books').all()
        ])
        description_ascii = unidecode.unidecode(description_original)[:200]

        body = {
            "Amount": int(amount),
            "CardType": "FINIK_QR",
            "PaymentId": payment_id,
            "RedirectUrl": REDIRECT_URL,
            "Data": {
                "accountId": ACCOUNT_ID,
                "merchantCategoryCode": FINIK_MCC,
                "name_en": f"Order-{order.id}",
                "description": description_ascii,
                "webhookUrl": WEBHOOK_URL,
            },
        }

        request_data = {
            "http_method": "POST",
            "path": "/v1/payment",
            "headers": {
                "Host": HOST,
                "x-api-key": API_KEY,
                "x-api-timestamp": timestamp,
            },
            "query_string_parameters": None,
            "body": body,
        }

        signature = Signer(**request_data).sign(PRIVATE_KEY_PEM)

        resp = requests.post(
            urljoin(BASE_URL, "/v1/payment"),
            headers={
                "content-type": "application/json",
                "x-api-key": API_KEY,
                "x-api-timestamp": timestamp,
                "signature": signature,
            },
            data=json.dumps(body, separators=(",", ":"), ensure_ascii=True),
            allow_redirects=False,
            timeout=10,
        )

        if resp.status_code in (301, 302, 303, 307, 308):
            return {
                "payment_id": payment_id,
                "payment_url": resp.headers.get("Location"),
                "status": "redirect",
            }
        elif resp.status_code == 201:
            return resp.json()
        else:
            raise Exception(f"Finik error {resp.status_code}: {resp.text}")

CONTACT_NUMBERS = {
    'БИШКЕК': '+996 (700) 777-244',
    'ОШ': '+996 (555) 444-011',
}

def handle_payment_success(pre_payment):
    order = pre_payment.order
    if order:
        order.status = 'Оплачен'
        order.save(update_fields=['status'])

        items = order.items.select_related('books').all()
        items_text = "\n".join([
            f"  • {item.books.books_name} — {item.quantity} даана x {item.price} сом = {item.total_price} сом"
            for item in items
        ])

        promo_text = (
            f'🎟️ Промокод: {order.promo_code.code} ({order.promo_code.discount_percent}% скидка)\n'
            if order.promo_code else ''
        )

        # Регионго жараша байланыш номери
        our_contact = CONTACT_NUMBERS.get(order.region.upper().strip(), '+996 (777) 444-011')

        send_mail(
            subject=f'✅ #{order.id} заказыңыз төлөндү',
            message=(
                f'Саламатсызбы, {order.user.username}!\n\n'
                f'#{order.id} номерлүү заказыңыз ийгиликтүү төлөндү.\n\n'
                f'📚 Заказдын курамы:\n{items_text}\n\n'
                f'💰 Жалпы сумма: {order.total_price} сом\n'
                f'{promo_text}'
                f'📍 Жеткирүү дареги: {order.address}\n'
                f'🏙️ Шаар: {order.region}\n'
                f'📞 Сиздин номериңиз: {order.phone_number}\n'
                f'🚚 Жеткирүү мөөнөтү: 1 кундун ичинде\n\n'
                f'❓ Суроолор болсо биз менен байланышыңыз:\n'
                f'📱 {our_contact}\n\n'
                f'Баалуу Китептен сатып алганыңызга чоң рахмат!'
            ),
            from_email=os.getenv('EMAIL_HOST_USER'),
            recipient_list=[order.user.email],
            fail_silently=True,
        )