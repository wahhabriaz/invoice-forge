from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from invoice_forge.models import Invoice, settings
from invoice_forge.logger import get_logger

log = get_logger(__name__)


def _get_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(settings.template_dir),
        autoescape=True,
    )


def render_html(invoice: Invoice) -> str:
    env = _get_env()
    tmpl = env.get_template("invoice.html")
    return tmpl.render(invoice=invoice)


def render_pdf(invoice: Invoice, output_path: Path | None = None) -> Path:
    out_dir = Path(settings.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    path = output_path or out_dir / f"invoice_{invoice.invoice_number}.pdf"
    html_content = render_html(invoice)

    HTML(string=html_content, base_url=str(out_dir)).write_pdf(str(path))
    log.info(f"PDF rendered → {path}")
    return path