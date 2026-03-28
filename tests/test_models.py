from decimal import Decimal
from datetime import date
import pytest
from invoice_forge.models import Invoice, LineItem, Address


def _base_invoice(**kwargs):
    defaults = dict(
        invoice_number="INV-001",
        issue_date=date(2026, 1, 1),
        due_date=date(2026, 2, 1),
        currency="USD",
        from_address=Address(name="Me", street="1 A St", city="NY", country="US"),
        to_address=Address(name="Client", street="2 B St", city="LA", country="US"),
        items=[LineItem(description="Work", quantity=Decimal("1"),
                        unit_price=Decimal("100"), tax_rate=Decimal("10"))],
    )
    defaults.update(kwargs)
    return Invoice(**defaults)


def test_line_item_subtotal():
    item = LineItem(description="X", quantity=Decimal("3"),
                    unit_price=Decimal("50"), tax_rate=Decimal("10"))
    assert item.subtotal == Decimal("150.00")
    assert item.tax_amount == Decimal("15.00")
    assert item.total == Decimal("165.00")


def test_invoice_grand_total_with_discount():
    inv = _base_invoice(discount_pct=Decimal("10"))
    # subtotal=100, tax=10, discount=10% of 100=10 → grand=100
    assert inv.grand_total == Decimal("100.00")


def test_due_date_before_issue_raises():
    with pytest.raises(ValueError):
        _base_invoice(issue_date=date(2026, 3, 1), due_date=date(2026, 1, 1))