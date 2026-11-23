import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product(product_name):
    """Создает продукт в Stripe.

    Принимает название продукта (курса или урока).
    Возвращает ID созданного продукта.
    """
    product = stripe.Product.create(name=product_name)
    return product.id


def create_stripe_price(amount_cents, product_id):
    """Создает цену в Stripe для указанного продукта.

    Принимает сумму В КОПЕЙКАХ (unit_amount — минимальная единица валюты:
    для рублей это копейки, поэтому вьюха уже передала amount * 100).
    Возвращает ID созданной цены.
    """
    price = stripe.Price.create(
        currency="rub",
        unit_amount=int(amount_cents),
        product=product_id,
    )
    return price.id


def create_stripe_session(price_id):
    """Создает сессию оплаты (Checkout Session).

    Принимает ID цены (price_...), а не ID продукта.
    Возвращает объект сессии: id — идентификатор сессии,
    url — ссылка на страницу оплаты.
    """
    session = stripe.checkout.Session.create(
        success_url="http://127.0.0.1:8000/",
        cancel_url="http://127.0.0.1:8000/",
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
    )
    return session


def retrieve_stripe_session(session_id):
    """Возвращает актуальные данные сессии по ее ID.

    Используется для проверки статуса платежа:
    session.status — open / complete / expired,
    session.payment_status — unpaid / paid.
    """
    return stripe.checkout.Session.retrieve(session_id)
