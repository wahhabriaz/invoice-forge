import smtplib
from email.message import EmailMessage
from pathlib import Path
from invoice_forge.models import Invoice, settings
from invoice_forge.logger import get_logger

log = get_logger(__name__)


def send_invoice(invoice: Invoice, pdf_path: Path) -> bool:
    if not all([settings.smtp_user, settings.smtp_pass, invoice.to_address.email]):
        log.warning("Email skipped — SMTP credentials or recipient email not set")
        return False

    msg = EmailMessage()
    msg["Subject"] = f"Invoice #{invoice.invoice_number} from {invoice.from_address.name}"
    msg["From"] = settings.smtp_from or settings.smtp_user
    msg["To"] = invoice.to_address.email

    msg.set_content(
        f"Dear {invoice.to_address.name},\n\n"
        f"Please find attached invoice #{invoice.invoice_number} "
        f"for {invoice.currency} {invoice.grand_total}.\n\n"
        f"Due date: {invoice.due_date}\n\n"
        f"Thank you for your business.\n\n"
        f"{invoice.from_address.name}"
    )

    pdf_bytes = pdf_path.read_bytes()
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf",
                       filename=pdf_path.name)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            smtp.starttls()
            smtp.login(settings.smtp_user, settings.smtp_pass)
            smtp.send_message(msg)
        log.info(f"Invoice emailed to {invoice.to_address.email}")
        return True
    except smtplib.SMTPException as exc:
        log.error(f"Email failed: {exc}")
        return False