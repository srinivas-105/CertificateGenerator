from app.models.certificate import Certificate
from app.models.job import GenerationJob


def test_one_failure_does_not_stop_other_certificates(client, test_app, monkeypatch):
    from app.services import job_processor

    original = job_processor.generate_certificate
    calls = {"count": 0}

    def generate_with_one_failure(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("intentional test failure")
        return original(*args, **kwargs)

    monkeypatch.setattr(job_processor, "generate_certificate", generate_with_one_failure)

    payload = {
        "organization_name": "Tech Academy",
        "course_name": "Backend Development",
        "issue_date": "2026-10-08",
        "recipients": [
            {"name": "First", "email": "first@example.com"},
            {"name": "Second", "email": "second@example.com"},
        ],
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 201

    job_id = response.json()["id"]
    job_response = client.get(f"/api/v1/jobs/{job_id}")
    assert job_response.json()["status"] == "COMPLETED_WITH_ERRORS"
    assert job_response.json()["success_count"] == 1
    assert job_response.json()["failure_count"] == 1

    certificates_response = client.get(f"/api/v1/jobs/{job_id}/certificates")
    statuses = [item["status"] for item in certificates_response.json()]
    assert sorted(statuses) == ["COMPLETED", "FAILED"]
