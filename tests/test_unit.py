import pytest

from models import Book, Cart, Order, PaymentGateway, User


@pytest.fixture
def sample_book():
    return Book("Sample", "Cat", 9.99, "/img")


def test_cart_add_and_total(sample_book):
    cart = Cart()
    cart.add_book(sample_book, 2)
    assert cart.get_total_items() == 2
    assert cart.get_total_price() == pytest.approx(19.98)


def test_cart_update_quantity_remove_on_zero(sample_book):
    cart = Cart()
    cart.add_book(sample_book, 1)
    cart.update_quantity(sample_book.title, 0)
    assert cart.is_empty()


def test_cart_update_quantity_invalid_ignored(sample_book):
    cart = Cart()
    cart.add_book(sample_book, 3)
    cart.update_quantity(sample_book.title, "not-a-number")
    assert cart.get_total_items() == 3


def test_payment_gateway_success_credit_card():
    result = PaymentGateway.process_payment({
        'payment_method': 'credit_card',
        'card_number': '4242424242424242',
        'expiry_date': '12/30',
        'cvv': '123',
    })
    assert result['success'] is True
    assert result['transaction_id']


def test_payment_gateway_failure_invalid_card():
    result = PaymentGateway.process_payment({
        'payment_method': 'credit_card',
        'card_number': '00001111',
        'expiry_date': '12/30',
        'cvv': '123',
    })
    assert result['success'] is False


def test_user_orders_and_history(sample_book):
    user = User("a@b.com", "pw", "Name", "Addr")
    order = Order("OID1", user.email, [type('CI', (), {'book': sample_book, 'quantity': 2})()], {}, {}, 19.98)
    user.add_order(order)
    history = user.get_order_history()
    assert len(history) == 1
    assert history[0].order_id == "OID1"


