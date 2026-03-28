# invoice-forge

![Python](https://img.shields.io/badge/python-3.11+-blue)
![PDF](https://img.shields.io/badge/PDF-WeasyPrint-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

> Generate professional PDF invoices and HTML/CSV reports from JSON or CSV data.
> Features Jinja2 templates, tax/discount calculations, batch processing, and SMTP email delivery.

## Features

- PDF generation with WeasyPrint + Jinja2 HTML templates
- Pydantic v2 data validation with computed tax, discount, and totals
- Load from JSON (single invoice) or CSV (batch)
- HTML + CSV summary reports
- Optional SMTP email delivery with PDF attachment
- Rich CLI — generate, batch, report commands

## Quick start

```bash
git clone https://github.com/wahhabriaz/invoice-forge
cd invoice-forge
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env

# Generate a single PDF
invoice-forge generate samples/sample_invoice.json

# Batch from CSV
invoice-forge batch samples/sample_invoices.csv

# Generate report
invoice-forge report samples/sample_invoices.csv --format both
```

## CLI commands

| Command                | Description                        |
| ---------------------- | ---------------------------------- |
| `generate <file.json>` | Generate PDF from a JSON invoice   |
| `batch <file.csv>`     | Generate PDFs for all CSV invoices |
| `report <file.csv>`    | Generate HTML + CSV summary report |

Add `--email` to any command to send the PDF via SMTP.
