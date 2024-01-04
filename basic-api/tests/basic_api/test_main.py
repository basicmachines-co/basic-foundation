import pytest
from fastapi.testclient import TestClient

from basic_api.main import app


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client  # testing happens here


def test_read_root(test_app):
    response = test_app.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
