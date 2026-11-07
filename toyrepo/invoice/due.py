"""Due dates for invoices."""

from datetime import date, timedelta


def due_date(issued: date, net_days: int) -> date:
    """Return the date payment is due: ``net_days`` after ``issued``.

    A due date never falls on a weekend; it moves to the following Monday.
    """
    due = issued + timedelta(days=net_days)
    # Seeded bug (due-date-weekend): only Sunday is rolled forward, so a due
    # date that lands on a Saturday stays on the Saturday.
    if due.weekday() == 6:
        due += timedelta(days=1)
    return due
