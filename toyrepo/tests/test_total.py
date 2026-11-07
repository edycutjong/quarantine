from decimal import Decimal

from invoice import invoice_total


def test_no_coupon():
    assert invoice_total(Decimal("100.00"), Decimal("0"), Decimal("10")) == Decimal("110.00")


def test_tax_is_charged_after_the_coupon():
    # (100.00 - 20.00) * 1.10 = 88.00
    assert invoice_total(Decimal("100.00"), Decimal("20.00"), Decimal("10")) == Decimal("88.00")
