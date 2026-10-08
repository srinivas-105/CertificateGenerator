def create_job(client):
    return client.post(
        "/api/v1/jobs",
        json={
            "organization_name": "Tech Academy",
            "course_name": "Backend Development",
            "issue_date": "2026-10-08",
            "recipients": [{"name": "Rahul Kumar", "email": "rahul@example.com"}],
        },
    )


def test_certificate_listing_and_download(client):
    response = create_job(client)
    job_id = response.json()["id"]

    certificates = client.get(f"/api/v1/jobs/{job_id}/certificates")
    assert certificates.status_code == 200
    certificate = certificates.json()[0]
    assert certificate["download_url"]

    download = client.get(certificate["download_url"])
    assert download.status_code == 200
    assert download.headers["content-type"] == "application/pdf"
    assert download.content.startswith(b"%PDF")


def test_missing_certificate_returns_404(client):
    response = client.get("/api/v1/certificates/does-not-exist/download")
    assert response.status_code == 404


def test_failed_certificate_cannot_be_downloaded(client, test_app, monkeypatch):
    from app.services import job_processor

    monkeypatch.setattr(job_processor, "generate_certificate", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("failed")))

    response = create_job(client)
    job_id = response.json()["id"]
    certificate = client.get(f"/api/v1/jobs/{job_id}/certificates").json()[0]

    download = client.get(f"/api/v1/certificates/{certificate['id']}/download")
    assert download.status_code == 409
