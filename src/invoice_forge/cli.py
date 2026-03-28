import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from invoice_forge.loader import load_from_json, load_from_csv
from invoice_forge.renderer import render_pdf
from invoice_forge.reporter import save_html_report, save_csv_report
from invoice_forge.mailer import send_invoice
from invoice_forge.logger import get_logger

console = Console()
log = get_logger(__name__)


def _print_summary(invoice):
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_row("Invoice #", f"[bold]{invoice.invoice_number}[/bold]")
    table.add_row("Client", invoice.to_address.name)
    table.add_row("Subtotal", f"{invoice.currency} {invoice.subtotal}")
    table.add_row("Tax", f"{invoice.currency} {invoice.total_tax}")
    if invoice.discount_pct:
        table.add_row("Discount", f"{invoice.discount_pct}%")
    table.add_row("Total Due", f"[green bold]{invoice.currency} {invoice.grand_total}[/green bold]")
    console.print(Panel(table, title="Invoice Summary", border_style="blue"))


@click.group()
@click.version_option("0.1.0", prog_name="invoice-forge")
def main():
    """Invoice Forge — PDF invoice and report generator."""
    pass


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--email", "-e", is_flag=True, help="Email the invoice to the client.")
@click.option("--output", "-o", default=None, help="Custom output PDF path.")
def generate(input_file, email, output):
    """Generate a PDF invoice from a JSON file."""
    console.rule("[bold blue]Invoice Forge[/bold blue]")
    try:
        invoice = load_from_json(input_file)
        out = Path(output) if output else None
        pdf_path = render_pdf(invoice, out)
        _print_summary(invoice)
        console.print(f"\n[green]✓[/green] PDF saved → [bold]{pdf_path}[/bold]")
        if email:
            ok = send_invoice(invoice, pdf_path)
            status = "[green]✓ Sent[/green]" if ok else "[yellow]! Skipped[/yellow]"
            console.print(f"Email: {status}")
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1)


@main.command()
@click.argument("csv_file", type=click.Path(exists=True))
@click.option("--email", "-e", is_flag=True, help="Email each invoice.")
def batch(csv_file, email):
    """Generate PDFs for all invoices in a CSV file."""
    console.rule("[bold blue]Batch Mode[/bold blue]")
    invoices = load_from_csv(csv_file)
    console.print(f"Found [bold]{len(invoices)}[/bold] invoices\n")
    for inv in invoices:
        pdf_path = render_pdf(inv)
        console.print(f"[green]✓[/green] {inv.invoice_number} → {pdf_path.name}")
        if email:
            send_invoice(inv, pdf_path)


@main.command()
@click.argument("csv_file", type=click.Path(exists=True))
@click.option("--format", "-f", "fmt",
              type=click.Choice(["html", "csv", "both"], case_sensitive=False),
              default="both", show_default=True)
def report(csv_file, fmt):
    """Generate an HTML and/or CSV summary report from a CSV file."""
    console.rule("[bold blue]Report Generator[/bold blue]")
    invoices = load_from_csv(csv_file)
    if fmt in ("html", "both"):
        p = save_html_report(invoices)
        console.print(f"[green]✓[/green] HTML report → [bold]{p}[/bold]")
    if fmt in ("csv", "both"):
        p = save_csv_report(invoices)
        console.print(f"[green]✓[/green] CSV report  → [bold]{p}[/bold]")