"""Testes automatizados para a API DevOps de Tarefas."""

import pytest
from fastapi.testclient import TestClient

from app.main import app, tasks


@pytest.fixture(autouse=True)
def reset_tasks():
    """Limpa a lista de tarefas antes de cada teste."""
    tasks.clear()
    yield
    tasks.clear()


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Testes do endpoint raiz
# ---------------------------------------------------------------------------


def test_root_retorna_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_root_retorna_mensagem(client):
    response = client.get("/")
    data = response.json()
    assert "message" in data
    assert data["message"] == "API DevOps em execucao"


def test_root_retorna_link_docs(client):
    response = client.get("/")
    data = response.json()
    assert "docs" in data


# ---------------------------------------------------------------------------
# Testes do endpoint de saude
# ---------------------------------------------------------------------------


def test_health_retorna_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_retorna_status_ok(client):
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


def test_health_retorna_versao(client):
    response = client.get("/health")
    data = response.json()
    assert "version" in data
    assert data["version"] == "1.0.0"


# ---------------------------------------------------------------------------
# Testes do endpoint GET /tasks
# ---------------------------------------------------------------------------


def test_listar_tarefas_retorna_200(client):
    response = client.get("/tasks")
    assert response.status_code == 200


def test_listar_tarefas_vazia(client):
    response = client.get("/tasks")
    assert response.json() == []


def test_listar_tarefas_apos_criacao(client):
    client.post("/tasks", json={"title": "Estudar Docker"})
    response = client.get("/tasks")
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Estudar Docker"


# ---------------------------------------------------------------------------
# Testes do endpoint POST /tasks
# ---------------------------------------------------------------------------


def test_criar_tarefa_retorna_201(client):
    response = client.post("/tasks", json={"title": "Configurar CI"})
    assert response.status_code == 201


def test_criar_tarefa_retorna_dados(client):
    response = client.post("/tasks", json={"title": "Configurar CI"})
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Configurar CI"
    assert data["done"] is False


def test_criar_multiplas_tarefas(client):
    client.post("/tasks", json={"title": "Tarefa Um"})
    client.post("/tasks", json={"title": "Tarefa Dois"})
    response = client.get("/tasks")
    assert len(response.json()) == 2


def test_criar_tarefa_titulo_muito_curto(client):
    response = client.post("/tasks", json={"title": "AB"})
    assert response.status_code == 422


def test_criar_tarefa_titulo_muito_longo(client):
    response = client.post("/tasks", json={"title": "A" * 81})
    assert response.status_code == 422


def test_criar_tarefa_sem_titulo(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Testes do endpoint PATCH /tasks/{id}/done
# ---------------------------------------------------------------------------


def test_concluir_tarefa_retorna_200(client):
    client.post("/tasks", json={"title": "Fazer deploy"})
    response = client.patch("/tasks/1/done")
    assert response.status_code == 200


def test_concluir_tarefa_muda_done_para_true(client):
    client.post("/tasks", json={"title": "Fazer deploy"})
    response = client.patch("/tasks/1/done")
    assert response.json()["done"] is True


def test_concluir_tarefa_inexistente_retorna_404(client):
    response = client.patch("/tasks/999/done")
    assert response.status_code == 404


def test_concluir_tarefa_preserva_dados(client):
    client.post("/tasks", json={"title": "Publicar no ECR"})
    response = client.patch("/tasks/1/done")
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Publicar no ECR"
    assert data["done"] is True
