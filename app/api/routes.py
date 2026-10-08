from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.certificate import Certificate, CertificateStatus
from app.models.job import GenerationJob
from app.schemas.job import CertificateResponse, JobCreateRequest, JobResponse, JobStatusResponse
from app.services.job_processor import process_job

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    request: JobCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> GenerationJob:
    job = GenerationJob(
        organization_name=request.organization_name,
        course_name=request.course_name,
        issue_date=request.issue_date,
        total_count=len(request.recipients),
    )
    job.certificates = [
        Certificate(recipient_name=recipient.name, recipient_email=str(recipient.email))
        for recipient in request.recipients
    ]

    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(process_job, job.id)
    return job


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str, db: Session = Depends(get_db)) -> JobStatusResponse:
    job = db.get(GenerationJob, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation job not found")

    completed_count = job.success_count + job.failure_count
    progress = round((completed_count / job.total_count) * 100, 2) if job.total_count else 0.0
    return JobStatusResponse.model_validate({**job.__dict__, "progress_percentage": progress})


@router.get("/jobs/{job_id}/certificates", response_model=list[CertificateResponse])
def list_certificates(job_id: str, db: Session = Depends(get_db)) -> list[CertificateResponse]:
    if db.get(GenerationJob, job_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation job not found")

    certificates = db.scalars(
        select(Certificate).where(Certificate.job_id == job_id).order_by(Certificate.created_at)
    ).all()
    return [
        CertificateResponse.model_validate(
            {
                **certificate.__dict__,
                "download_url": (
                    f"{settings.api_v1_prefix}/certificates/{certificate.id}/download"
                    if certificate.status == CertificateStatus.COMPLETED
                    else None
                ),
            }
        )
        for certificate in certificates
    ]


@router.get("/certificates/{certificate_id}/download")
def download_certificate(certificate_id: str, db: Session = Depends(get_db)) -> FileResponse:
    certificate = db.get(Certificate, certificate_id)
    if certificate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")

    if certificate.status != CertificateStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Certificate is not available for download",
        )

    if not certificate.file_path:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Certificate file path is missing",
        )

    file_path = Path(certificate.file_path)
    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Generated certificate file is missing",
        )

    return FileResponse(path=file_path, media_type="application/pdf", filename=f"{certificate.id}.pdf")
