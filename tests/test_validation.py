def valid_payload():
    return {
        "organization_name": "Tech Academy",
        "course_name": "Python Backend Development",
        "issue_date": "2026-10-08",
        "recipients": [{"name": "Rahul Kumar", "email": "rahul@gmail.com"}],
    }


def test_empty_recipients_returns_422(client):
    payload = valid_payload()
    payload["recipients"] = []
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422


def test_whitespace_recipient_name_returns_422(client):
    payload = valid_payload()
    payload["recipients"][0]["name"] = "   "
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422


def test_invalid_email_returns_422(client):
    payload = valid_payload()
    payload["recipients"][0]["email"] = "not-an-email"
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422


def test_too_many_recipients_returns_422(client, monkeypatch):
    monkeypatch.setattr("app.core.config.settings.max_recipients_per_job", 2)
    payload = valid_payload()
    payload["recipients"] = [
        {"name": "One", "email": "one@example.com"},
        {"name": "Two", "email": "two@example.com"},
        {"name": "Three", "email": "three@example.com"},
    ]
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422
