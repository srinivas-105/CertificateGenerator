from app.models.certificate import Certificate, CertificateStatus
from app.models.job import GenerationJob, JobStatus


def test_job_progress_and_final_status(client, test_app):
    payload = {
        "organization_name": "Tech Academy",
        "course_name": "Backend Development",
        "issue_date": "2026-10-08",
        "recipients": [
            {"name": "One", "email": "one@example.com"},
            {"name": "Two", "email": "two@example.com"},
        ],
    }
    response = client.post("/api/v1/jobs", json=payload)
    job_id = response.json()["id"]

    status_response = client.get(f"/api/v1/jobs/{job_id}")
    assert status_response.status_code == 200
    assert status_response.json()["progress_percentage"] == 100.0
    assert status_response.json()["status"] == "COMPLETED"


def test_missing_job_returns_404(client):
    response = client.get("/api/v1/jobs/does-not-exist")
    assert response.status_code == 404
