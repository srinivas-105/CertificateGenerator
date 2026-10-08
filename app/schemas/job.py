from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.config import settings
from app.models.certificate import CertificateStatus
from app.models.job import JobStatus


class RecipientInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("recipient name cannot be empty")
        return value


class JobCreateRequest(BaseModel):
    organization_name: str = Field(min_length=1, max_length=150)
    course_name: str = Field(min_length=1, max_length=200)
    issue_date: date
    recipients: list[RecipientInput] = Field(min_length=1, max_length=settings.max_recipients_per_job)

    @field_validator("recipients")
    @classmethod
    def validate_recipient_limit(cls, value: list[RecipientInput]) -> list[RecipientInput]:
        if len(value) > settings.max_recipients_per_job:
            raise ValueError(f"recipients cannot exceed {settings.max_recipients_per_job}")
        return value

    @field_validator("organization_name", "course_name")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value cannot be empty")
        return value


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_name: str
    course_name: str
    issue_date: date
    status: JobStatus
    total_count: int
    success_count: int
    failure_count: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class JobStatusResponse(JobResponse):
    progress_percentage: float


class CertificateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    recipient_name: str
    recipient_email: str
    status: CertificateStatus
    download_url: str | None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None
