from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Order, OrderItem


# ─── Создание заказа из корзины ────────────────────────────────────────────────

@transaction.atomic
def create_order_from_cart(user, phone_number, address):
    if not user.is_authenticated:
        raise ValidationError("Необходимо авторизоваться")

    cart = user.cart

    if not cart.items.exists():
        raise ValidationError("Корзина пуста")

    order = Order.objects.create(
        user=user,
        phone_number=phone_number,
        address=address,
        promo_code=cart.promo_code,
    )

    for item in cart.items.select_related('books'):
        OrderItem.objects.create(
            order=order,
            books=item.books,
            price=item.books.get_actual_price() or Decimal('0.00'),
            quantity=item.quantity,
        )

    order.calculate_total()

    cart.items.all().delete()
    cart.promo_code = None
    cart.save(update_fields=['promo_code'])

    return order
