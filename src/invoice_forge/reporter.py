import csv
from pathlib import Path
from jinja2 import Environment, BaseLoader
from invoice_forge.models import Invoice, settings
from invoice_forge.logger import get_logger

log = get_logger(__name__)

REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/>
<style>
  body{font-family:Arial,sans-serif;padding:32px;color:#1a1a1a}
  h1{color:#2c3e50;margin-bottom:24px}
  table{width:100%;border-collapse:collapse}
  th{background:#2c3e50;color:#fff;padding:8px 12px;text-align:left}
  td{padding:8px 12px;border-bottom:1px solid #eee}
  tr:nth-child(even){background:#f8f9fa}
  .total{font-weight:700;color:#2c3e50}
  .summary{margin-top:24px;padding:16px;background:#f0f4f8;border-radius:6px}
</style>
</head>
<body>
<h1>Invoice Report</h1>
<table>
  <thead><tr>
    <th>Invoice #</th><th>Client</th><th>Issue Date</th>
    <th>Due Date</th><th>Currency</th><th>Grand Total</th>
  </tr></thead>
  <tbody>
  {% for inv in invoices %}
  <tr>
    <td>{{ inv.invoice_number }}</td>
    <td>{{ inv.to_address.name }}</td>
    <td>{{ inv.issue_date }}</td>
    <td>{{ inv.due_date }}</td>
    <td>{{ inv.currency }}</td>
    <td class="total">{{ "%.2f"|format(inv.grand_total) }}</td>
  </tr>
  {% endfor %}
  </tbody>
</table>
<div class="summary">
  <strong>Total invoices:</strong> {{ invoices|length }} &nbsp;|&nbsp;
  <strong>Combined value:</strong> {{ "%.2f"|format(total) }}
</div>
</body></html>"""


def save_html_report(invoices: list[Invoice], filename: str = "report.html") -> Path:
    out = Path(settings.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / filename

    env = Environment(loader=BaseLoader(), autoescape=True)
    tmpl = env.from_string(REPORT_TEMPLATE)
    total = sum(inv.grand_total for inv in invoices)
    path.write_text(tmpl.render(invoices=invoices, total=total), encoding="utf-8")
    log.info(f"HTML report → {path}")
    return path


def save_csv_report(invoices: list[Invoice], filename: str = "report.csv") -> Path:
    out = Path(settings.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / filename

    fields = ["invoice_number", "client", "issue_date", "due_date",
              "currency", "subtotal", "tax", "discount", "grand_total"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for inv in invoices:
            w.writerow({
                "invoice_number": inv.invoice_number,
                "client": inv.to_address.name,
                "issue_date": inv.issue_date,
                "due_date": inv.due_date,
                "currency": inv.currency,
                "subtotal": float(inv.subtotal),
                "tax": float(inv.total_tax),
                "discount": float(inv.discount_amount),
                "grand_total": float(inv.grand_total),
            })
    log.info(f"CSV report → {path}")
    return path