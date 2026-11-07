"""A tiny invoicing package with three seeded bugs (see tests/)."""

from .discount import apply_discount
from .due import due_date
from .total import invoice_total

__all__ = ["apply_discount", "due_date", "invoice_total"]
