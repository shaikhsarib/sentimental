import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"

def test_create_project():
    response = client.post("/api/projects", json={
        "name": "Test Project",
        "description": "Integration Test"
    })
    assert response.status_code == 200
    data = response.json()
    assert "project_id" in data
    return data["project_id"]

def test_add_document():
    project_id = test_create_project()
    response = client.post(f"/api/projects/{project_id}/documents/text", json={
        "title": "Test Doc",
        "content": "This is a test content about a brand crisis.",
        "content_type": "text"
    })
    assert response.status_code == 200
    assert "doc_id" in response.json()

def test_build_graph():
    project_id = test_create_project()
    client.post(f"/api/projects/{project_id}/documents/text", json={
        "title": "Test Doc",
        "content": "Pepsi and Kendall Jenner protest imagery.",
        "content_type": "text"
    })
    response = client.post(f"/api/projects/{project_id}/graph/build")
    assert response.status_code == 200
    assert "nodes" in response.json()
