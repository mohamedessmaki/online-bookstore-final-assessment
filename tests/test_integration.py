import pytest

from app import BOOKS, app, cart, users


@pytest.fixture
def client():
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test',
    })
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_index_page_loads(client):
    res = client.get('/')
    assert res.status_code == 200
    for b in BOOKS:
        assert b.title in res.get_data(as_text=True)


def test_add_to_cart_and_view(client):
    cart.clear()
    res = client.post('/add-to-cart', data={'title': BOOKS[0].title, 'quantity': '2'}, follow_redirects=True)
    assert res.status_code == 200
    res = client.get('/cart')
    assert BOOKS[0].title in res.get_data(as_text=True)


def test_update_cart_invalid_quantity_graceful(client):
    cart.clear()
    client.post('/add-to-cart', data={'title': BOOKS[0].title, 'quantity': '1'})
    res = client.post('/update-cart', data={'title': BOOKS[0].title, 'quantity': 'abc'}, follow_redirects=True)
    assert res.status_code == 200


def test_checkout_flow_success_credit_card(client):
    cart.clear()
    client.post('/add-to-cart', data={'title': BOOKS[1].title, 'quantity': '3'})
    res = client.get('/checkout')
    assert res.status_code == 200
    res = client.post('/process-checkout', data={
        'name': 'John',
        'email': 'john@example.com',
        'address': '123 St',
        'city': 'NY',
        'zip_code': '10001',
        'payment_method': 'credit_card',
        'card_number': '4242424242424242',
        'expiry_date': '12/30',
        'cvv': '123',
        'discount_code': 'save10',  # case-insensitive
    }, follow_redirects=False)
    assert res.status_code in (302, 303)
    # Follow redirect to confirmation
    res2 = client.get(res.headers['Location'])
    assert res2.status_code == 200


def test_checkout_empty_cart_redirects(client):
    cart.clear()
    res = client.post('/process-checkout', data={}, follow_redirects=False)
    assert res.status_code in (302, 303)


def test_register_and_login_logout_flow(client):
    # Register
    res = client.post('/register', data={
        'email': 'newuser@example.com',
        'password': 'pw',
        'name': 'New User',
        'address': 'Addr'
    }, follow_redirects=True)
    assert res.status_code == 200
    # Logout
    res = client.get('/logout', follow_redirects=True)
    assert res.status_code == 200
    # Login
    res = client.post('/login', data={'email': 'newuser@example.com', 'password': 'pw'}, follow_redirects=True)
    assert res.status_code == 200


def test_account_requires_login(client):
    res = client.get('/account')
    # Should redirect to login
    assert res.status_code in (302, 303)


