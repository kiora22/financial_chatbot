import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the path so we can import from our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Financial Assistant API is running"}


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "version" in response.json()


def test_chat_endpoint():
    """Test the chat endpoint."""
    payload = {
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "user_id": "test_user"
    }
    response = client.post("/api/v1/chat/", json=payload)
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"]["role"] == "assistant"
    assert "content" in response.json()["message"]


def test_budget_categories_endpoint():
    """Test the budget categories endpoint."""
    response = client.get("/api/v1/budget/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # In Phase 1, we're returning mock data, so we should have at least one category
    assert len(response.json()) > 0
    assert "name" in response.json()[0]


def test_budget_line_items_endpoint():
    """Test the budget line items endpoint."""
    response = client.get("/api/v1/budget/line-items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # In Phase 1, we're returning mock data, so we should have at least one line item
    assert len(response.json()) > 0
    assert "name" in response.json()[0]
    assert "amount" in response.json()[0]