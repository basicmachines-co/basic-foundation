from typing import AsyncGenerator, Generator

import pytest
from foundation.app import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)


def test_read_root(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
