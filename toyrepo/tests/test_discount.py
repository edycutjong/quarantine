from invoice import apply_discount


def test_round_number_discount():
    assert apply_discount(100.00, 25) == 75.00


def test_half_price_rounds_half_up():
    assert apply_discount(19.99, 50) == 10.00


def test_half_price_odd_cents():
    assert apply_discount(20.09, 50) == 10.05
