import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from src.models.schemas import TicketTriageOutput, CategoryEnum, UrgencyEnum, DepartmentEnum
from src.models.db_models import UserModel
from src.api.deps import get_current_user, require_admin

# Mock del usuario autenticado normal
from src.models.db_models import RoleEnum  # Ajusta la importación según la ruta de tu proyecto

def mock_get_current_user():
    return UserModel(id=1, email="user@example.com", role=RoleEnum.USER)

def mock_require_admin():
    return UserModel(id=2, email="admin@example.com", role=RoleEnum.ADMIN)


def test_create_ticket_endpoint(client: TestClient):
    """Prueba el endpoint POST /api/v1/triage simulando la respuesta del LLM y la autenticación."""
    # Mapear la dependencia de autenticación del router
    client.app.dependency_overrides[get_current_user] = mock_get_current_user

    payload = {
        "description": "Se cayó la red en la oficina central",
        "provider": "local"
    }

    mock_triage = TicketTriageOutput(
        category=CategoryEnum.IT,
        urgency=UrgencyEnum.HIGH,
        summary="Caída general de red",
        department=DepartmentEnum.IT_SUPPORT,
        thought_process="1. Fallo crítico de red. 2. Regla IT."
    )

    # Simular la llamada pesada/externa al LLM
    with patch("src.api.endpoints.tickets.process_triage_with_llm") as mock_llm:
        mock_llm.return_value = (mock_triage, 1.2, 150)

        response = client.post("/api/v1/triage", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Caída general de red"
    assert data["provider"] == "local"


def test_get_tickets_list_endpoint(client: TestClient):
    """Prueba el endpoint GET /api/v1/tickets simulando un usuario con rol ADMIN."""
    client.app.dependency_overrides[require_admin] = mock_require_admin

    response = client.get("/api/v1/tickets")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_my_tickets_endpoint(client: TestClient):
    """Prueba el endpoint GET /api/v1/tickets/me para usuarios normales."""
    client.app.dependency_overrides[get_current_user] = mock_get_current_user

    response = client.get("/api/v1/tickets/me")

    assert response.status_code == 200
    assert isinstance(response.json(), list)