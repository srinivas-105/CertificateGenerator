import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.certificate import Certificate, CertificateStatus
from app.models.job import GenerationJob, JobStatus
from app.services.certificate_generator import generate_certificate

logger = logging.getLogger(__name__)


def process_job(job_id: str) -> None:
    db = SessionLocal()
    try:
        job = db.get(GenerationJob, job_id)
        if job is None:
            logger.error("Generation job %s was not found", job_id)
            return

        job.status = JobStatus.PROCESSING
        job.started_at = datetime.now(timezone.utc)
        db.commit()

        certificates = db.scalars(
            select(Certificate).where(
                Certificate.job_id == job_id,
                Certificate.status == CertificateStatus.PENDING,
            )
        ).all()

        for certificate in certificates:
            certificate.status = CertificateStatus.PROCESSING
            db.commit()

            try:
                file_path = generate_certificate(
                    output_directory=settings.output_directory,
                    certificate_id=certificate.id,
                    organization_name=job.organization_name,
                    course_name=job.course_name,
                    recipient_name=certificate.recipient_name,
                    issue_date=job.issue_date,
                )
                certificate.file_path = file_path
                certificate.status = CertificateStatus.COMPLETED
                certificate.completed_at = datetime.now(timezone.utc)
                job.success_count += 1
            except (OSError, ValueError, RuntimeError) as exc:
                certificate.status = CertificateStatus.FAILED
                certificate.error_message = str(exc)
                certificate.completed_at = datetime.now(timezone.utc)
                job.failure_count += 1
                logger.exception("Certificate %s failed", certificate.id)
            except Exception as exc:
                certificate.status = CertificateStatus.FAILED
                certificate.error_message = str(exc)
                certificate.completed_at = datetime.now(timezone.utc)
                job.failure_count += 1
                logger.exception("Unexpected certificate generation failure for %s", certificate.id)

            db.commit()

        if job.success_count == job.total_count:
            job.status = JobStatus.COMPLETED
        elif job.success_count > 0 and job.failure_count > 0:
            job.status = JobStatus.COMPLETED_WITH_ERRORS
        else:
            job.status = JobStatus.FAILED

        job.completed_at = datetime.now(timezone.utc)
        db.commit()
    except Exception:
        logger.exception("Generation job %s failed before completion", job_id)
        db.rollback()
        job = db.get(GenerationJob, job_id)
        if job is not None:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()
