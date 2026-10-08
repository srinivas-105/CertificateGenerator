# Certificate Generation API

## How to use
after running the application go to docs endpoint
we can see health, jobs, {job_id}, certificates, download
click on jobs and give the json and you will get something like 
{
  "id": "a7dccb9e-5f51-473d-84f0-5f9109f4d562",
  "organization_name": "TCS",
  "course_name": "NQT digital",
  "issue_date": "2026-10-08",
  "status": "QUEUED",
  "total_count": 1,
  "success_count": 0,
  "failure_count": 0,
  "created_at": "2026-10-08T15:40:50.709675",
  "started_at": null,
  "completed_at": null
}

copy the id and try it in certificates [
  {
    "id": "065d93cb-930e-46f7-ab75-b5bc9f49292f",
    "recipient_name": "Marati Srinivasa Rao",
    "recipient_email": "m.srinivasarao051@gmail.com",
    "status": "COMPLETED",
    "download_url": "/api/v1/certificates/065d93cb-930e-46f7-ab75-b5bc9f49292f/download",
    "error_message": null,
    "created_at": "2026-10-08T15:40:50.731811",
    "completed_at": "2026-10-08T15:40:50.777873"
  }
]
copy that id and paste it in download certificates and you will have the certificate

## Overview

Certificate Generation API is a small FastAPI backend for creating personalized completion certificates in bulk. A client submits an organization, course, issue date, and recipient list. The API creates a generation job, stores one certificate record for each recipient, and processes the PDFs in the background.

The project is intentionally focused on backend fundamentals: request validation, relational data modeling, background processing, PDF generation, failure isolation, and API testing.

## Problem

Generating certificates one at a time is repetitive when a course or event has many recipients. This API accepts a single bulk request and creates one PDF certificate per recipient using the same predefined certificate design.

A job tracks the overall progress while each certificate keeps its own status. This means a failure for one recipient can be recorded without stopping the rest of the batch.

## Features

- Bulk certificate generation through one API request
- Pydantic request validation
- SQLite database with SQLAlchemy 2.x
- UUID-based job and certificate identifiers
- One predefined landscape A4 certificate template
- ReportLab PDF generation
- FastAPI BackgroundTasks for lightweight asynchronous processing
- Per-certificate success and failure tracking
- Job progress percentage
- Certificate listing
- PDF download endpoint
- Automated API and service tests
- Configurable database and output directory through environment variables

## Tech Stack

| Technology | Purpose |
| --- | --- |
| Python 3.12+ | Application language |
| FastAPI | HTTP API and OpenAPI/Swagger documentation |
| Uvicorn | ASGI development server |
| Pydantic 2 | Request and response validation |
| pydantic-settings | Environment configuration |
| SQLAlchemy 2 | Database access and ORM |
| SQLite | Simple local relational database |
| ReportLab | PDF certificate generation |
| Pytest | Automated tests |
| HTTPX | FastAPI test client support |

## Architecture

```text
Client
  |
  v
FastAPI
  |
  v
Pydantic Validation
  |
  v
Create Generation Job
  |
  v
Background Processing
  |
  v
Certificate Generator
  |
  +------> PDF Files
  |
  v
SQLite / SQLAlchemy
```

The API layer handles HTTP concerns. Pydantic validates input before database work begins. The service layer performs certificate generation and job processing. SQLAlchemy models store the state needed to retrieve and monitor jobs.

## Project Structure

```text
certificate-generator-api/
|
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── job.py
│   │   └── certificate.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── job.py
│   └── services/
│       ├── __init__.py
│       ├── certificate_generator.py
│       └── job_processor.py
|
├── templates/
│   └── certificate_template.py
├── generated_certificates/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_job_creation.py
│   ├── test_validation.py
│   ├── test_certificate_generation.py
│   ├── test_job_status.py
│   ├── test_partial_failure.py
│   └── test_download.py
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── RUN.md
```

## Data Model

### GenerationJob

`GenerationJob` represents one bulk request. It stores the organization, course, issue date, overall status, recipient count, success count, failure count, and timestamps.

### Certificate

`Certificate` represents one recipient's certificate. It stores the recipient's name and email, its processing status, generated file path, error information, and timestamps.

A generation job has a one-to-many relationship with certificates:

```text
GenerationJob 1 -------- * Certificate
```

The database stores the file path only as server-side metadata. API responses expose a download URL instead of an internal filesystem path.

## Processing Flow

```text
POST /api/v1/jobs
        |
        v
Validate request
        |
        v
Create GenerationJob
        |
        v
Create Certificate records as PENDING
        |
        v
Commit transaction
        |
        v
Return HTTP 201
        |
        v
FastAPI BackgroundTasks
        |
        v
Mark job PROCESSING
        |
        v
Process each certificate independently
        |
        +----> Generate PDF ----> COMPLETED
        |
        +----> Generation error -> FAILED
        |
        v
Update counters and final job status
        |
        v
Retrieve job / certificates / PDF
```

The initial database transaction is committed before background processing starts. The background task creates its own SQLAlchemy session, so it does not reuse the request's database session.

## Status Handling

### Job statuses

- `QUEUED`: the job was created and is waiting for processing.
- `PROCESSING`: certificate generation is in progress.
- `COMPLETED`: every certificate succeeded.
- `COMPLETED_WITH_ERRORS`: at least one certificate succeeded and at least one failed.
- `FAILED`: all certificates failed or the job failed before meaningful processing could complete.

### Certificate statuses

- `PENDING`: the certificate record exists but has not started processing.
- `PROCESSING`: PDF generation is currently running.
- `COMPLETED`: the PDF was generated successfully.
- `FAILED`: PDF generation failed and the error was stored on the certificate record.

## Partial Failure Handling

Each certificate is processed inside its own small try/except block. A generation error changes only that certificate to `FAILED`, stores the error message, increments the job failure count, and then processing continues with the next certificate.

For example, if a job contains ten recipients and one certificate fails, the other nine can still complete. The final job status becomes `COMPLETED_WITH_ERRORS` when there is at least one success and at least one failure.

If every certificate fails, the final job status is `FAILED`.

## API Documentation

### GET `/health`

Checks that the API process is running.

Response:

```json
{
  "status": "ok"
}
```

Status codes:

- `200`: API is running.

### POST `/api/v1/jobs`

Creates a bulk certificate generation job.

Example request:

```json
{
  "organization_name": "Tech Academy",
  "course_name": "Python Backend Development",
  "issue_date": "2026-10-08",
  "recipients": [
    {
      "name": "Rahul Kumar",
      "email": "rahul@gmail.com"
    },
    {
      "name": "Srinivasa Rao",
      "email": "srinivas@gmail.com"
    },
    {
      "name": "Anjali Sharma",
      "email": "anjali@gmail.com"
    }
  ]
}
```

Example response:

```json
{
  "id": "8f6b7d5a-1c0e-4c34-8d5c-3e1d7a5f8c20",
  "organization_name": "Tech Academy",
  "course_name": "Python Backend Development",
  "issue_date": "2026-10-08",
  "status": "QUEUED",
  "total_count": 3,
  "success_count": 0,
  "failure_count": 0,
  "created_at": "2026-10-08T10:30:00",
  "started_at": null,
  "completed_at": null
}
```

Status codes:

- `201`: job created.
- `422`: request validation failed.

### GET `/api/v1/jobs/{job_id}`

Returns job information and current progress.

Example response:

```json
{
  "id": "8f6b7d5a-1c0e-4c34-8d5c-3e1d7a5f8c20",
  "organization_name": "Tech Academy",
  "course_name": "Python Backend Development",
  "issue_date": "2026-10-08",
  "status": "PROCESSING",
  "total_count": 100,
  "success_count": 45,
  "failure_count": 2,
  "created_at": "2026-10-08T10:30:00",
  "started_at": "2026-10-08T10:30:01",
  "completed_at": null,
  "progress_percentage": 47.0
}
```

Progress is calculated as:

```text
(success_count + failure_count) / total_count * 100
```

Status codes:

- `200`: job found.
- `404`: job does not exist.

### GET `/api/v1/jobs/{job_id}/certificates`

Lists all certificates belonging to a job.

Example response:

```json
[
  {
    "id": "d6c6cb3b-b5c0-44dd-bb16-4e2a7d72c3bb",
    "recipient_name": "Rahul Kumar",
    "recipient_email": "rahul@gmail.com",
    "status": "COMPLETED",
    "download_url": "/api/v1/certificates/d6c6cb3b-b5c0-44dd-bb16-4e2a7d72c3bb/download",
    "error_message": null,
    "created_at": "2026-10-08T10:30:00",
    "completed_at": "2026-10-08T10:30:02"
  }
]
```

The internal file path is not exposed.

Status codes:

- `200`: job exists and certificates are returned.
- `404`: job does not exist.

### GET `/api/v1/certificates/{certificate_id}/download`

Downloads a completed certificate PDF.

Status codes:

- `200`: PDF returned.
- `404`: certificate does not exist.
- `409`: certificate has not completed successfully.
- `500`: database says the certificate is complete but its file is missing.

## Example Responses

### QUEUED

```json
{
  "status": "QUEUED",
  "total_count": 3,
  "success_count": 0,
  "failure_count": 0,
  "progress_percentage": 0.0
}
```

### PROCESSING

```json
{
  "status": "PROCESSING",
  "total_count": 3,
  "success_count": 1,
  "failure_count": 0,
  "progress_percentage": 33.33
}
```

### COMPLETED

```json
{
  "status": "COMPLETED",
  "total_count": 3,
  "success_count": 3,
  "failure_count": 0,
  "progress_percentage": 100.0
}
```

### COMPLETED_WITH_ERRORS

```json
{
  "status": "COMPLETED_WITH_ERRORS",
  "total_count": 3,
  "success_count": 2,
  "failure_count": 1,
  "progress_percentage": 100.0
}
```

## Certificate Generation

ReportLab creates a landscape A4 PDF directly. The predefined template contains the organization name, certificate title, recipient name, completion text, course name, issue date, and two signature areas.

The output filename is based only on the generated certificate UUID. Recipient-provided names are never used as filesystem paths.

The template uses standard ReportLab fonts to keep the project self-contained. Common Latin characters and punctuation are supported without adding external font files.

## Validation

The API validates organization and course names after trimming whitespace. Recipient names are trimmed and must contain at least one character. Recipient emails use Pydantic's `EmailStr`. A job must contain at least one recipient and is limited by `MAX_RECIPIENTS_PER_JOB`.

FastAPI returns normal HTTP `422` validation responses for invalid request bodies.

Duplicate recipient names are allowed. Two different people can have the same name.

## Database

SQLite is used for local development because it requires no separate database server. The SQLAlchemy engine reads `DATABASE_URL` from environment configuration, so a PostgreSQL URL can be supplied later without changing the model or route code.

Tables are created automatically at application startup for this assignment. A migration framework is intentionally not included because schema migrations are outside the required scope.

## Background Processing Decision

FastAPI `BackgroundTasks` is used because it keeps the assignment lightweight and allows the POST request to return without waiting for every PDF to finish.

The background processor creates its own database session and processes certificates one at a time. This is appropriate for a small local assignment, but it is not a durable distributed job queue.

For a larger production system, a queue such as Celery or RQ with dedicated workers would be a better fit. That is future scope rather than an implemented feature here.

## Error Handling

Request validation is handled by Pydantic and FastAPI. Missing jobs and certificates return `404`. A certificate that is not successfully generated cannot be downloaded as a completed PDF. If a database record says a certificate is complete but the PDF has disappeared, the download endpoint returns a clear `500` response instead of exposing an internal path or crashing.

Certificate generation failures are isolated to the individual certificate and recorded in `error_message`.

## Testing

The test suite covers:

- valid job creation
- database certificate creation
- empty recipient validation
- whitespace-only names
- invalid email addresses
- maximum recipient validation
- direct PDF generation
- generated file existence
- completed certificate status
- job progress calculation
- final job status
- partial certificate failure
- continued processing after a failure
- certificate listing
- successful PDF download
- missing certificate handling
- failed certificate download handling

Tests use a temporary SQLite database and temporary output directory. They do not require files from the developer's machine or network access.

Run the tests with:

```powershell
pytest
```

## Setup

See `RUN.md` for Windows PowerShell commands from environment creation through testing.

## Running

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

## Swagger

After starting the server, open:

```text
http://127.0.0.1:8000/docs
```

The Swagger UI can be used to create jobs, inspect progress, list certificates, and download generated PDFs.

## Learning

This project provides practical experience with:

- FastAPI API design
- Pydantic validation
- SQLAlchemy relationships
- bulk processing
- background tasks
- PDF generation
- failure isolation
- API testing
- environment-based configuration

It is designed to demonstrate understanding of these backend concepts rather than claim advanced production expertise.

## Future Scope

The following are possible improvements and are not implemented in this version:

- PostgreSQL for a multi-instance deployment
- a durable queue such as Celery or RQ
- object storage for generated PDFs
- authentication and authorization
- email delivery
- retry policies for transient generation failures
- idempotency for repeated requests
- application metrics and monitoring
- a larger worker-based architecture for high-volume batches

## Limitations

The current version uses local filesystem storage and FastAPI background tasks. If the process stops while a job is being processed, in-flight work is not automatically resumed. This is a deliberate trade-off for a small, locally runnable assignment.
#   C e r t i f i c a t e G e n e r a t o r  
 