"""Percentage discounts on a price."""


def apply_discount(price: float, percent: float) -> float:
    """Return ``price`` reduced by ``percent`` percent, rounded to cents.

    Money should round half-up to the cent (19.99 at 50% off is 10.00).
    """
    # Seeded bug (discount-rounding): float multiplication plus round() rounds
    # an inexact binary value, so some prices come out 0.01 low.
    return round(price * (1 - percent / 100), 2)
