from pathlib import Path

from templates.certificate_template import draw_certificate


def generate_certificate(
    output_directory: str,
    certificate_id: str,
    organization_name: str,
    course_name: str,
    recipient_name: str,
    issue_date,
) -> str:
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"{certificate_id}.pdf"

    draw_certificate(
        output_path=file_path,
        organization_name=organization_name,
        course_name=course_name,
        recipient_name=recipient_name,
        issue_date=issue_date,
    )
    return str(file_path)
