# src/api/endpoints/tickets.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.database.connection import get_db
from src.models.schemas import TicketResponseDB, StatsResponse, TicketUpdate, TicketRequest, TicketResponse
from src.crud import ticket_crud
from src.services.triage_service import process_triage_with_llm
from src.api.deps import get_current_user, require_admin
from src.models.db_models import UserModel
from src.core.logging_config import logger  # Tu logger centralizado

router = APIRouter(prefix="/api/v1", tags=["Tickets"])


# -------------------------------------------------------------------
# 🔓/🔐 1. POST /triage (Crear Incidencia)
# Permitido para CUALQUIER USUARIO AUTENTICADO (USER o ADMIN)
# -------------------------------------------------------------------
@router.post("/triage", response_model=TicketResponse)
async def triage_ticket(
    ticket_request: TicketRequest, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)  # Requiere JWT válido
):
    logger.info(f"📥 [POST /triage] Usuario ID: {current_user.id} solicitó triaje con proveedor: {ticket_request.provider}")
    
    triage_output, latency, tokens = process_triage_with_llm(ticket_request)
    
    new_ticket = ticket_crud.create_ticket_record(
        db, ticket_request.description, ticket_request.provider, triage_output, latency, tokens, user_id=current_user.id
    )
    logger.info(f"💾 [DB Success] Creado registro de ticket ID: {getattr(new_ticket, 'id', 'N/A')} en la base de datos.")

    return TicketResponse(
        category=triage_output.category, urgency=triage_output.urgency,
        summary=triage_output.summary, department=triage_output.department,
        thought_process=triage_output.thought_process, latency=latency,
        tokens_consumed=tokens, provider=ticket_request.provider
    )


# -------------------------------------------------------------------
# 🔒 2. GET /tickets (Ver Listado de Tickets)
# SOLO PERMITIDO PARA ADMINISTRADORES
# -------------------------------------------------------------------
@router.get("/tickets", response_model=List[TicketResponseDB])
def get_tickets(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)  # Requiere JWT y Rol ADMIN
):
    logger.info(f"📥 [GET /tickets] Admin ID: {current_user.id} solicitando listado completo de tickets.")
    tickets = ticket_crud.fetch_all_tickets(db, skip, limit)
    logger.info(f"📤 [DB Success] Se recuperaron {len(tickets)} tickets globales.")
    
    return [
        TicketResponseDB(
            id=t.id, description=t.description, provider=t.provider,
            urgency=t.urgency, summary=t.summary, department_name=dept_name,
            thought_process=t.thought_process, latency=t.latency,
            tokens_consumed=t.tokens_consumed, created_at=t.created_at
        ) for t, dept_name in tickets
    ]


# -------------------------------------------------------------------
# 🔒 3. GET /stats (Estadísticas Globales)
# SOLO PERMITIDO PARA ADMINISTRADORES
# -------------------------------------------------------------------
@router.get("/stats", response_model=StatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)  # Requiere JWT y Rol ADMIN
):
    logger.info(f"📥 [GET /stats] Admin ID: {current_user.id} consultando estadísticas globales.")
    stats = ticket_crud.fetch_stats_data(db)
    logger.info(f"📤 [DB Success] Estadísticas calculadas: {stats}")
    return stats


# -------------------------------------------------------------------
# 🔒 4. PATCH /tickets/{ticket_id} (Reasignar o Modificar Ticket)
# SOLO PERMITIDO PARA ADMINISTRADORES
# -------------------------------------------------------------------
@router.patch("/tickets/{ticket_id}", response_model=TicketResponseDB)
def update_ticket(
    ticket_id: int, 
    ticket_update: TicketUpdate, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)  # Requiere JWT y Rol ADMIN
):
    logger.info(f"📥 [PATCH /tickets/{ticket_id}] Admin ID: {current_user.id} intentando actualizar ticket.")
    logger.info(f"📦 [Payload entrante] {ticket_update.model_dump(exclude_unset=True)}")

    ticket = ticket_crud.get_ticket_by_id(db, ticket_id)
    if not ticket:
        logger.warning(f"❌ [404 Not Found] El ticket #{ticket_id} no existe en la base de datos.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket #{ticket_id} no encontrado")
    
    try:
        updated_ticket, dept_name = ticket_crud.update_ticket_record(db, ticket, ticket_update)
        logger.info(f"✅ [DB Success] Ticket #{ticket_id} actualizado con éxito. Departamento: {dept_name}, Urgencia: {updated_ticket.urgency}")
    except ValueError as e:
        logger.error(f"❌ [400 Bad Request] Error de validación al actualizar ticket #{ticket_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return TicketResponseDB(
        id=updated_ticket.id, description=updated_ticket.description, provider=updated_ticket.provider,
        urgency=updated_ticket.urgency, summary=updated_ticket.summary, department_name=dept_name,
        thought_process=updated_ticket.thought_process, latency=updated_ticket.latency,
        tokens_consumed=updated_ticket.tokens_consumed, created_at=updated_ticket.created_at
    )


# -------------------------------------------------------------------
# 🔐 5. GET /tickets/me (Ver historial de tickets del usuario actual)
# PERMITIDO PARA CUALQUIER USUARIO AUTENTICADO (USER o ADMIN)
# -------------------------------------------------------------------
@router.get("/tickets/me", response_model=List[TicketResponseDB])
def get_my_tickets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)  # Requiere JWT válido
):
    logger.info(f"📥 [GET /tickets/me] Usuario ID: {current_user.id} solicitando su historial de tickets.")
    tickets = ticket_crud.fetch_user_tickets(db, user_id=current_user.id, skip=skip, limit=limit)
    logger.info(f"📤 [DB Success] Se recuperaron {len(tickets)} tickets propios para el usuario ID {current_user.id}.")
    
    return [
        TicketResponseDB(
            id=t.id,
            description=t.description,
            provider=t.provider,
            urgency=t.urgency,
            summary=t.summary,
            department_name=dept_name,
            thought_process=t.thought_process,
            latency=t.latency,
            tokens_consumed=t.tokens_consumed,
            created_at=t.created_at
        ) for t, dept_name in tickets
    ]