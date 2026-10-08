import importlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: tests that exercise the API and background processing")


@pytest.fixture
def test_app(tmp_path, monkeypatch):
    db_url = "sqlite://"
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    monkeypatch.setattr("app.db.session.engine", engine)
    monkeypatch.setattr("app.db.session.SessionLocal", session_local)
    monkeypatch.setattr("app.services.job_processor.SessionLocal", session_local)
    monkeypatch.setattr("app.core.config.settings.output_directory", str(tmp_path / "generated"))

    from app.db.base import Base
    from app.models import Certificate, GenerationJob
    Base.metadata.create_all(bind=engine)

    import app.main
    importlib.reload(app.main)
    app = app.main.app

    yield app, session_local, tmp_path

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(test_app):
    app, _, _ = test_app
    with TestClient(app) as test_client:
        yield test_client
