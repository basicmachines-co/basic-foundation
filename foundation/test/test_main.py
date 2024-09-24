from typing import AsyncGenerator

import pytest
from foundation.app import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def test_app() -> AsyncGenerator[TestClient, None, None]:
    client = TestClient(app)
    yield client  # testing happens here


def test_read_root(test_app):
    response = test_app.get("/")
    assert response.status_code == 200
