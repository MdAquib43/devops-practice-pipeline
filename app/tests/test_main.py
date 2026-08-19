from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_and_get_task():
    r = client.post("/tasks", json={"title": "Set up CI/CD", "done": False})
    assert r.status_code == 201
    task_id = r.json()["id"]

    r = client.get(f"/tasks/{task_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Set up CI/CD"


def test_update_task():
    r = client.post("/tasks", json={"title": "Deploy to k8s"})
    task_id = r.json()["id"]

    r = client.put(f"/tasks/{task_id}", json={"title": "Deploy to k8s", "done": True})
    assert r.status_code == 200
    assert r.json()["done"] is True


def test_delete_task():
    r = client.post("/tasks", json={"title": "Temp task"})
    task_id = r.json()["id"]

    r = client.delete(f"/tasks/{task_id}")
    assert r.status_code == 204

    r = client.get(f"/tasks/{task_id}")
    assert r.status_code == 404


def test_get_missing_task():
    r = client.get("/tasks/9999")
    assert r.status_code == 404
