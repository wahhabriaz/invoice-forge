import csv
import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from invoice_forge.models import Invoice, LineItem, Address
from invoice_forge.logger import get_logger

log = get_logger(__name__)


def load_from_json(path: str | Path) -> Invoice:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    invoice = Invoice.model_validate(data)
    log.info(f"Loaded invoice {invoice.invoice_number} from JSON")
    return invoice


def load_from_csv(path: str | Path) -> list[Invoice]:
    """
    CSV format — one row per line item. Rows sharing the same
    invoice_number are grouped into a single Invoice.
    Required columns:
      invoice_number, issue_date, due_date, currency,
      from_name, from_street, from_city, from_country, from_email,
      to_name, to_street, to_city, to_country, to_email,
      description, quantity, unit_price, tax_rate, discount_pct, notes
    """
    rows: dict[str, list[dict]] = {}
    with Path(path).open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = row["invoice_number"]
            rows.setdefault(key, []).append(row)

    invoices = []
    for inv_num, lines in rows.items():
        first = lines[0]
        try:
            invoice = Invoice(
                invoice_number=inv_num,
                issue_date=date.fromisoformat(first["issue_date"]),
                due_date=date.fromisoformat(first["due_date"]),
                currency=first.get("currency", "USD"),
                discount_pct=Decimal(first.get("discount_pct", "0")),
                notes=first.get("notes") or None,
                from_address=Address(
                    name=first["from_name"], street=first["from_street"],
                    city=first["from_city"], country=first["from_country"],
                    email=first.get("from_email"),
                ),
                to_address=Address(
                    name=first["to_name"], street=first["to_street"],
                    city=first["to_city"], country=first["to_country"],
                    email=first.get("to_email"),
                ),
                items=[
                    LineItem(
                        description=r["description"],
                        quantity=Decimal(r["quantity"]),
                        unit_price=Decimal(r["unit_price"]),
                        tax_rate=Decimal(r.get("tax_rate", "0")),
                    )
                    for r in lines
                ],
            )
            invoices.append(invoice)
            log.info(f"Loaded invoice {inv_num} from CSV")
        except Exception as exc:
            log.error(f"Skipping invoice {inv_num}: {exc}")

    return invoices