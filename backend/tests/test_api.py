import pytest
from fastapi.testclient import TestClient
from main import app
import os
import json

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"

def test_list_projects():
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_project():
    payload = {"name": "Test Project", "description": "A project for testing"}
    response = client.post("/api/projects", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert "project_id" in data

def test_add_document_validation():
    # Test MAX_CONTENT_CHARS validation
    long_content = "X" * 50001
    payload = {"title": "Long Doc", "content": long_content}
    # We need a project_id first
    p_res = client.post("/api/projects", json={"name": "Validation Test"})
    pid = p_res.json()["project_id"]
    
    response = client.post(f"/api/projects/{pid}/documents/text", json=payload)
    assert response.status_code == 400
    assert "Content too long" in response.json()["detail"]
