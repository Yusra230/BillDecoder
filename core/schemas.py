from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field


ChargeType = Literal[
    "energy",
    "fixed",
    "fpa",
    "quarterly_adjustment",
    "surcharge",
    "meter_rent",
    "subsidy",
    "other",
]

TaxType = Literal[
    "gst",
    "electricity_duty",
    "income_tax",
    "municipal_tax",
    "other_tax",
]


class ChargeItem(BaseModel):
    type: ChargeType = Field(
        ...,
        description="One of: energy, fixed, fpa, quarterly_adjustment, surcharge, meter_rent, subsidy, other",
    )
    amount: float = Field(
        ...,
        description="Charge amount in PKR. Negative for subsidies or deductions.",
    )


class TaxItem(BaseModel):
    type: TaxType = Field(
        ...,
        description="One of: gst, electricity_duty, income_tax, municipal_tax, other_tax",
    )
    amount: float = Field(
        ...,
        description="Tax amount in PKR.",
    )


class Level1BillJSON(BaseModel):
    provider: Optional[Literal["KE", "LESCO", "IESCO"]] = Field(
        None, description="One of KE, LESCO, or IESCO"
    )
    tariff: Optional[str] = Field(
        None, description="Tariff code exactly as printed, e.g., A1-R, A-1a(01)"
    )
    sanctioned_load_kw: Optional[Union[int, float]] = Field(
        None, description="Sanctioned load in kW"
    )
    bill_month: Optional[str] = Field(
        None, description="Billing month in YYYY-MM format"
    )
    reading_date: Optional[str] = Field(
        None, description="Reading date in YYYY-MM-DD format"
    )
    issue_date: Optional[str] = Field(
        None, description="Issue date in YYYY-MM-DD format"
    )
    due_date: Optional[str] = Field(
        None, description="Due date in YYYY-MM-DD format without late surcharge"
    )
    previous_reading: Optional[Union[int, float]] = Field(
        None, description="Previous meter reading"
    )
    current_reading: Optional[Union[int, float]] = Field(
        None, description="Current meter reading"
    )
    units_consumed: Optional[Union[int, float]] = Field(
        None, description="Units billed for the current month"
    )
    charges: List[ChargeItem] = Field(
        default_factory=list,
        description="Itemized charges. Empty list [] if none or not printed.",
    )
    total_charges: Optional[Union[int, float]] = Field(
        None, description="Printed charges subtotal or null"
    )
    taxes: List[TaxItem] = Field(
        default_factory=list,
        description="Itemized taxes. Empty list [] if only combined tax is printed.",
    )
    total_taxes: Optional[Union[int, float]] = Field(
        None, description="Printed tax subtotal or null"
    )
    current_bill: Optional[Union[int, float]] = Field(
        None, description="Printed amount for current month's bill"
    )
    arrears: Optional[Union[int, float]] = Field(
        None, description="Previous dues carried forward (preserve sign, negative for CR credit)"
    )
    payable_within_due_date: Optional[Union[int, float]] = Field(
        None, description="Amount payable within due date"
    )
    payable_after_due_date: Optional[Union[int, float]] = Field(
        None, description="Amount payable after due date (highest if multiple)"
    )


def clean_num(val):
    """Normalize number representation: ints have no decimal point, floats rounded to 2 decimals."""
    if val is None:
        return None
    try:
        f = float(val)
        if f.is_integer():
            return int(f)
        return round(f, 2)
    except (ValueError, TypeError):
        return val


def format_bill_dict(data: dict) -> dict:
    """Ensure every required key is present and numbers are clean."""
    keys = [
        "provider",
        "tariff",
        "sanctioned_load_kw",
        "bill_month",
        "reading_date",
        "issue_date",
        "due_date",
        "previous_reading",
        "current_reading",
        "units_consumed",
        "charges",
        "total_charges",
        "taxes",
        "total_taxes",
        "current_bill",
        "arrears",
        "payable_within_due_date",
        "payable_after_due_date",
    ]
    out = {}
    for k in keys:
        v = data.get(k)
        if k in [
            "sanctioned_load_kw",
            "previous_reading",
            "current_reading",
            "units_consumed",
            "total_charges",
            "total_taxes",
            "current_bill",
            "arrears",
            "payable_within_due_date",
            "payable_after_due_date",
        ]:
            out[k] = clean_num(v)
        elif k == "charges":
            formatted_charges = []
            for item in (v or []):
                amt = clean_num(item.get("amount", 0))
                if amt == 0 or amt == 0.0:
                    continue  # Rule: Skip lines printed as 0
                formatted_charges.append({
                    "type": item.get("type", "other"),
                    "amount": amt,
                })
            out[k] = formatted_charges
        elif k == "taxes":
            formatted_taxes = []
            for item in (v or []):
                formatted_taxes.append({
                    "type": item.get("type", "other_tax"),
                    "amount": clean_num(item.get("amount", 0)),
                })
            out[k] = formatted_taxes
        else:
            out[k] = v
    return out
