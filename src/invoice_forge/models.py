from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="IF_")

    output_dir: str = "./output"
    template_dir: str = "./templates"
    log_level: str = "INFO"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_from: str = ""


settings = Settings()


class Address(BaseModel):
    name: str
    street: str
    city: str
    country: str
    email: str | None = None


class LineItem(BaseModel):
    description: str
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100)

    @property
    def subtotal(self) -> Decimal:
        return (self.quantity * self.unit_price).quantize(Decimal("0.01"), ROUND_HALF_UP)

    @property
    def tax_amount(self) -> Decimal:
        return (self.subtotal * self.tax_rate / 100).quantize(Decimal("0.01"), ROUND_HALF_UP)

    @property
    def total(self) -> Decimal:
        return self.subtotal + self.tax_amount


class Invoice(BaseModel):
    invoice_number: str
    issue_date: date
    due_date: date
    from_address: Address
    to_address: Address
    items: list[LineItem] = Field(min_length=1)
    discount_pct: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    notes: str | None = None
    currency: str = "USD"

    @model_validator(mode="after")
    def due_after_issue(self) -> "Invoice":
        if self.due_date < self.issue_date:
            raise ValueError("due_date must be on or after issue_date")
        return self

    @property
    def subtotal(self) -> Decimal:
        return sum(i.subtotal for i in self.items)

    @property
    def total_tax(self) -> Decimal:
        return sum(i.tax_amount for i in self.items)

    @property
    def discount_amount(self) -> Decimal:
        return (self.subtotal * self.discount_pct / 100).quantize(Decimal("0.01"), ROUND_HALF_UP)

    @property
    def grand_total(self) -> Decimal:
        return (self.subtotal + self.total_tax - self.discount_amount).quantize(
            Decimal("0.01"), ROUND_HALF_UP
        )