from pathlib import Path

from app.services.certificate_generator import generate_certificate


def test_valid_recipient_produces_pdf(tmp_path):
    file_path = generate_certificate(
        output_directory=str(tmp_path),
        certificate_id="8b5d2c90-0c61-4c62-9d74-fb1d79a9f6b1",
        organization_name="Tech Academy",
        course_name="Python Backend Development",
        recipient_name="José García",
        issue_date=__import__("datetime").date(2026, 10, 8),
    )

    path = Path(file_path)
    assert path.exists()
    assert path.suffix == ".pdf"
    assert path.read_bytes().startswith(b"%PDF")
