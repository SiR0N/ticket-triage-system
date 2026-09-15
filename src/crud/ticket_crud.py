# src/crud/ticket_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Tuple, Optional
from src.models.db_models import TicketModel, DepartmentModel
from src.models.schemas import TicketUpdate, UrgencyEnum

def get_ticket_by_id(db: Session, ticket_id: int) -> Optional[TicketModel]:
    return db.query(TicketModel).filter(TicketModel.id == ticket_id).first()

def get_department_by_code(db: Session, code: str) -> Optional[DepartmentModel]:
    return db.query(DepartmentModel).filter(DepartmentModel.code == code).first()

def get_department_by_name(db: Session, name: str) -> Optional[DepartmentModel]:
    return db.query(DepartmentModel).filter_by(name=name).first()

def update_ticket_record(db: Session, ticket: TicketModel, ticket_update: TicketUpdate) -> Tuple[TicketModel, str]:
    if ticket_update.urgency:
        ticket.urgency = ticket_update.urgency

    dept_name = ticket.department.name if ticket.department else "Sin asignar"
    
    if ticket_update.department_name:
        department = get_department_by_name(db, ticket_update.department_name)
        if not department:
            raise ValueError(f"El departamento '{ticket_update.department_name}' no existe.")
        ticket.department_id = department.id
        dept_name = department.name

    db.commit()
    db.refresh(ticket)
    return ticket, dept_name

def fetch_all_tickets(db: Session, skip: int = 0, limit: int = 100) -> List[Tuple[TicketModel, str]]:
    return (
        db.query(TicketModel, DepartmentModel.name.label("department_name"))
        .join(DepartmentModel, TicketModel.department_id == DepartmentModel.id)
        .order_by(TicketModel.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def fetch_stats_data(db: Session) -> dict:
    total = db.query(TicketModel).count()
    if total == 0:
        return {
            "total_tickets": 0, "avg_latency": 0.0, "avg_tokens": 0,
            "top_urgency": "N/A", "top_department": "N/A",
            "tickets_by_department": {}, "tickets_by_urgency": {}
        }

    avg_lat = db.query(func.avg(TicketModel.latency)).scalar() or 0.0
    avg_tok = db.query(func.avg(TicketModel.tokens_consumed)).scalar() or 0

    dept_counts = (
        db.query(DepartmentModel.name, func.count(TicketModel.id))
        .join(TicketModel, DepartmentModel.id == TicketModel.department_id)
        .group_by(DepartmentModel.name)
        .all()
    )
    by_dept = {name: count for name, count in dept_counts}

    urgency_counts = (
        db.query(TicketModel.urgency, func.count(TicketModel.id))
        .group_by(TicketModel.urgency)
        .all()
    )
    by_urgency = {urg.value if hasattr(urg, 'value') else str(urg): count for urg, count in urgency_counts}

    return {
        "total_tickets": total,
        "avg_latency": round(avg_lat, 2),
        "avg_tokens": int(avg_tok),
        "top_urgency": max(by_urgency, key=by_urgency.get) if by_urgency else "N/A",
        "top_department": max(by_dept, key=by_dept.get) if by_dept else "N/A",
        "tickets_by_department": by_dept,
        "tickets_by_urgency": by_urgency
    }

def create_ticket_record(db: Session, original_description: str, provider: str, triage_output, latency: float, tokens: int, user_id: int) -> TicketModel:
    dept_enum_name = triage_output.department.name
    department_record = get_department_by_code(db, dept_enum_name)
    department_id = department_record.id if department_record else None

    ticket_record = TicketModel(
        description=original_description,
        provider=provider,
        category=triage_output.category,
        urgency=triage_output.urgency,
        summary=triage_output.summary,
        department_id=department_id,
        thought_process=triage_output.thought_process,
        latency=latency,
        tokens_consumed=tokens,
        user_id=user_id
    )
    db.add(ticket_record)
    db.commit()
    db.refresh(ticket_record)
    return ticket_record

def fetch_user_tickets(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene los tickets creados por un usuario específico junto con el nombre de su departamento.
    """
    return (
        db.query(TicketModel, DepartmentModel.name)
        .join(DepartmentModel, TicketModel.department_id == DepartmentModel.id)
        .filter(TicketModel.user_id == user_id)
        .order_by(TicketModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )