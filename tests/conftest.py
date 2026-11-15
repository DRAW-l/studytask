import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "DATABASE": str(tmp_path / "studytask-test.db"),
        }
    )
    yield application


@pytest.fixture
def client(app):
    return app.test_client()
