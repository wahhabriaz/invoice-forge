import pdfkit
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from invoice_forge.models import settings
from invoice_forge.models import Invoice
from invoice_forge.logger import get_logger

log = get_logger(__name__)

import shutil
import os

_DEFAULT_PATHS = [
    r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
    r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
]

def _find_wkhtmltopdf() -> str:
    # Check PATH first
    found = shutil.which("wkhtmltopdf")
    if found:
        return found
    # Check common install locations
    for p in _DEFAULT_PATHS:
        if os.path.isfile(p):
            return p
    raise FileNotFoundError(
        "wkhtmltopdf not found. Install from https://wkhtmltopdf.org/downloads.html"
    )

WKHTMLTOPDF_PATH = _find_wkhtmltopdf()

PDF_OPTIONS = {
    "page-size": "A4",
    "margin-top": "0mm",
    "margin-right": "0mm",
    "margin-bottom": "0mm",
    "margin-left": "0mm",
    "encoding": "UTF-8",
    "no-outline": None,
    "quiet": "",
}


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

    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    pdfkit.from_string(html_content, str(path), options=PDF_OPTIONS, configuration=config)

    log.info(f"PDF rendered → {path}")
    return path