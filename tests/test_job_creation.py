from app.models.certificate import CertificateStatus
from app.models.job import JobStatus


def payload():
    return {
        "organization_name": "Tech Academy",
        "course_name": "Python Backend Development",
        "issue_date": "2026-10-08",
        "recipients": [
            {"name": "Rahul Kumar", "email": "rahul@gmail.com"},
            {"name": "Srinivasa Rao", "email": "srinivas@gmail.com"},
        ],
    }


def test_create_job_returns_201_and_creates_records(client, test_app):
    response = client.post("/api/v1/jobs", json=payload())

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == JobStatus.QUEUED
    assert data["total_count"] == 2

    _, session_local, _ = test_app
    with session_local() as db:
        from app.models.certificate import Certificate
        from app.models.job import GenerationJob

        job = db.get(GenerationJob, data["id"])
        certificates = db.query(Certificate).filter(Certificate.job_id == data["id"]).all()
        assert job is not None
        assert len(certificates) == 2
        assert all(c.status == CertificateStatus.COMPLETED for c in certificates)
