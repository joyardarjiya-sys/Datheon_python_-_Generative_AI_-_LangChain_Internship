from __future__ import annotations

from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr


Number = Union[StrictFloat, StrictInt]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)


class ExtractRequest(StrictModel):
    document_type: Literal["invoice", "resume"]
    provider: Literal["gemini", "gemini_fallback", "auto"] = "auto"
    text: StrictStr = Field(min_length=1, max_length=12_000)
    guidance: StrictStr = Field(default="", max_length=1_000)


class InvoiceLineItem(StrictModel):
    description: StrictStr
    quantity: Number
    unit_price: Number
    amount: Number


class InvoiceData(StrictModel):
    invoice_number: StrictStr | None
    vendor_name: StrictStr | None
    invoice_date: StrictStr | None
    due_date: StrictStr | None
    currency: StrictStr | None
    subtotal: Number | None
    tax: Number | None
    total: Number | None
    line_items: list[InvoiceLineItem] = Field(default_factory=list, max_length=50)
    payment_terms: StrictStr | None


class ResumeExperience(StrictModel):
    company: StrictStr
    title: StrictStr
    start_date: StrictStr | None
    end_date: StrictStr | None
    bullets: list[StrictStr] = Field(default_factory=list, max_length=20)


class ResumeEducation(StrictModel):
    institution: StrictStr
    degree: StrictStr | None
    field_of_study: StrictStr | None
    graduation_year: StrictStr | None


class ResumeData(StrictModel):
    full_name: StrictStr
    email: StrictStr | None
    phone: StrictStr | None
    location: StrictStr | None
    summary: StrictStr | None
    skills: list[StrictStr] = Field(default_factory=list, max_length=100)
    experience: list[ResumeExperience] = Field(default_factory=list, max_length=30)
    education: list[ResumeEducation] = Field(default_factory=list, max_length=20)


class Verification(StrictModel):
    status: Literal["verified"]
    checks: list[StrictStr]
    note: StrictStr
