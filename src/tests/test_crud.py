import pytest
from sqlalchemy.orm import Session
from src.crud import ticket_crud
from src.models.schemas import (
    TicketTriageOutput,
    TicketUpdate,
    CategoryEnum,
    UrgencyEnum,
    DepartmentEnum,
)

def test_create_ticket_record(db_session: Session):
    mock_triage_output = TicketTriageOutput(
        category=CategoryEnum.IT,
        urgency=UrgencyEnum.MEDIUM,
        summary="Problema de conexión al correo",
        department=DepartmentEnum.IT_SUPPORT,
        thought_process="1. Problema de correo. 2. Aplica regla IT."
    )

    ticket = ticket_crud.create_ticket_record(
        db=db_session,
        original_description="No puedo acceder a mi correo",
        provider="local",
        triage_output=mock_triage_output,
        latency=1.25,
        tokens=150,
        user_id=1
    )

    assert ticket.id is not None
    assert ticket.department_id is not None  # Valida que se asoció correctamente
    assert ticket.department_id == 1
    assert ticket.description == "No puedo acceder a mi correo"

def test_fetch_stats_data(db_session: Session):
    mock_triage = TicketTriageOutput(
        category=CategoryEnum.IT,
        urgency=UrgencyEnum.HIGH,
        summary="Servidor caído",
        department=DepartmentEnum.IT_SUPPORT,
        thought_process="1. Caída crítica."
    )

    ticket_crud.create_ticket_record(db_session, "Servidor 1", "local", mock_triage, 2.0, 200, 1)
    ticket_crud.create_ticket_record(db_session, "Servidor 2", "gemini", mock_triage, 4.0, 400, 1)

    stats = ticket_crud.fetch_stats_data(db_session)

    assert stats["total_tickets"] == 2
    assert stats["avg_latency"] == 3.0
    assert stats["avg_tokens"] == 300
    assert stats["top_department"] == "Soporte TI"