from datetime import date

from invoice import due_date


def test_weekday_due_date_unchanged():
    # Thu 1 Oct 2026 + 7 days = Thu 8 Oct 2026
    assert due_date(date(2026, 10, 1), 7) == date(2026, 10, 8)


def test_sunday_moves_to_monday():
    # Thu 1 Oct 2026 + 10 days = Sun 11 Oct -> Mon 12 Oct
    assert due_date(date(2026, 10, 1), 10) == date(2026, 10, 12)


def test_saturday_moves_to_monday():
    # Thu 1 Oct 2026 + 9 days = Sat 10 Oct -> Mon 12 Oct
    assert due_date(date(2026, 10, 1), 9) == date(2026, 10, 12)
