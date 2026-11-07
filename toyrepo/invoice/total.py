"""Invoice totals: coupon discount and sales tax."""

from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def invoice_total(subtotal: Decimal, coupon: Decimal, tax_percent: Decimal) -> Decimal:
    """Return the amount due.

    The coupon comes off the subtotal first; tax is charged on what is left.
    """
    # Seeded bug (tax-on-discounted): tax is charged on the full subtotal and
    # the coupon is taken off afterwards, so the customer pays tax on money
    # they never spent.
    taxed = subtotal * (1 + tax_percent / 100)
    return (taxed - coupon).quantize(CENT, rounding=ROUND_HALF_UP)
