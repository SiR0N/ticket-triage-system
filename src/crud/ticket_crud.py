# src/crud/ticket_crud.py
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.db_models import TicketModel, DepartmentModel, UserModel
from src.models.schemas import TicketUpdate, UrgencyEnum, TicketTriageOutput
from src.core.logging_config import logger


def get_ticket_by_id(db: Session, ticket_id: int) -> Optional[TicketModel]:
    logger.info(f"🔍 [CRUD] Buscando ticket por ID: {ticket_id}")
    ticket = db.query(TicketModel).filter(TicketModel.id == ticket_id).first()
    if ticket:
        logger.info(f"✅ [CRUD] Ticket encontrado (ID: {ticket.id}, User ID: {ticket.user_id})")
    else:
        logger.warning(f"⚠️ [CRUD] Ticket con ID {ticket_id} no existe en la base de datos.")
    return ticket


def get_department_by_code(db: Session, code: str) -> Optional[DepartmentModel]:
    logger.info(f"🔍 [CRUD] Buscando departamento por código: '{code}'")
    dept = db.query(DepartmentModel).filter(DepartmentModel.code == code).first()
    if dept:
        logger.info(f"✅ [CRUD] Departamento hallado por código: '{dept.name}' (ID: {dept.id})")
    else:
        logger.info(f"ℹ️ [CRUD] No se encontró departamento con código: '{code}'")
    return dept


def get_department_by_name(db: Session, name: str) -> Optional[DepartmentModel]:
    logger.info(f"🔍 [CRUD] Buscando departamento por nombre: '{name}'")
    dept = db.query(DepartmentModel).filter_by(name=name).first()
    if dept:
        logger.info(f"✅ [CRUD] Departamento hallado por nombre: '{dept.name}' (ID: {dept.id})")
    else:
        logger.info(f"ℹ️ [CRUD] No se encontró departamento con nombre: '{name}'")
    return dept


def update_ticket_record(db: Session, ticket: TicketModel, ticket_update: TicketUpdate) -> Tuple[TicketModel, str]:
    logger.info(f"📝 [CRUD] Actualizando ticket ID {ticket.id} | Datos recibidos: {ticket_update.model_dump(exclude_unset=True)}")

    if ticket_update.urgency:
        ticket.urgency = ticket_update.urgency
        logger.info(f"🔄 [CRUD] Urgencia actualizada a: {ticket.urgency}")

    dept_name = ticket.department.name if ticket.department else "Sin asignar"

    if ticket_update.department_name:
        department = get_department_by_name(db, ticket_update.department_name)
        if not department:
            logger.error(f"❌ [CRUD] El departamento '{ticket_update.department_name}' no existe en la base de datos.")
            raise ValueError(f"El departamento '{ticket_update.department_name}' no existe.")
        ticket.department_id = department.id
        dept_name = department.name
        logger.info(f"🔄 [CRUD] Departamento asignado a ID {department.id} ('{dept_name}')")

    db.commit()
    db.refresh(ticket)
    logger.info(f"💾 [CRUD] Cambios guardados con éxito para ticket ID {ticket.id}")
    return ticket, dept_name


def fetch_all_tickets(db: Session, skip: int = 0, limit: int = 100) -> List[Tuple[TicketModel, str, str]]:
    logger.info(f"📥 [CRUD] Solicitando listado global de tickets (skip={skip}, limit={limit})")
    
    results = (
        db.query(
            TicketModel, 
            DepartmentModel.name.label("department_name"),
            UserModel.email.label("user_email")
        )
        .outerjoin(DepartmentModel, TicketModel.department_id == DepartmentModel.id)
        .outerjoin(UserModel, TicketModel.user_id == UserModel.id)
        .order_by(TicketModel.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    logger.info(f"📊 [CRUD] Total de registros recuperados: {len(results)}")
    
    # Inspeccionamos detalladamente los primeros registros recuperados para diagnosticar el JOIN
    for i, (t, dept_name, u_email) in enumerate(results[:3], start=1):
        logger.info(
            f"   🔹 Ticket #{i} -> ID: {t.id} | "
            f"user_id DB: {t.user_id} | "
            f"user_email JOIN: '{u_email}' | "
            f"Dept: '{dept_name}'"
        )
        
    return results


def fetch_stats_data(db: Session) -> dict:
    logger.info("📊 [CRUD] Calculando métricas y estadísticas de la plataforma...")
    total = db.query(TicketModel).count()
    if total == 0:
        logger.warning("⚠️ [CRUD] Base de datos de tickets vacía. Devolviendo métricas en cero.")
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

    stats = {
        "total_tickets": total,
        "avg_latency": round(avg_lat, 2),
        "avg_tokens": int(avg_tok),
        "top_urgency": max(by_urgency, key=by_urgency.get) if by_urgency else "N/A",
        "top_department": max(by_dept, key=by_dept.get) if by_dept else "N/A",
        "tickets_by_department": by_dept,
        "tickets_by_urgency": by_urgency
    }
    logger.info(f"✅ [CRUD] Estadísticas calculadas: {stats}")
    return stats


def create_ticket_record(
    db: Session, 
    original_description: str, 
    provider: str, 
    triage_output, 
    latency: float, 
    tokens: int, 
    user_id: int
) -> TicketModel:
    logger.info(f"➕ [CRUD] Creando nuevo ticket en DB para user_id: {user_id} | Proveedor: '{provider}'")
    
    # 1. Resolver valores del departamento de forma segura
    dept_enum = triage_output.department
    dept_val = dept_enum.value if hasattr(dept_enum, "value") else str(dept_enum)
    dept_name = dept_enum.name if hasattr(dept_enum, "name") else str(dept_enum)

    # 2. Buscar registro del departamento
    department_record = (
        get_department_by_code(db, dept_name)
        or get_department_by_name(db, dept_val)
        or get_department_by_name(db, dept_name)
    )

    # 3. Crear departamento dinámicamente si falta en la base de datos
    if not department_record:
        logger.warning(f"⚠️ [CRUD] Departamento '{dept_val}' no existía. Creándolo dinámicamente...")
        department_record = DepartmentModel(name=dept_val, code=dept_name)
        db.add(department_record)
        db.flush()
        logger.info(f"✅ [CRUD] Departamento creado con ID: {department_record.id}")

    ticket_record = TicketModel(
        description=original_description,
        provider=provider,
        category=triage_output.category,
        urgency=triage_output.urgency,
        summary=triage_output.summary,
        department_id=department_record.id,
        thought_process=triage_output.thought_process,
        latency=latency,
        tokens_consumed=tokens,
        user_id=user_id
    )
    db.add(ticket_record)
    db.commit()
    db.refresh(ticket_record)
    
    logger.info(f"✨ [CRUD] Ticket guardado con exito. Nuevo ID: {ticket_record.id} asociado a User ID: {ticket_record.user_id}")
    return ticket_record


def fetch_user_tickets(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    logger.info(f"📥 [CRUD] Obteniendo tickets privados para el User ID: {user_id}")
    results = (
        db.query(TicketModel, DepartmentModel.name)
        .join(DepartmentModel, TicketModel.department_id == DepartmentModel.id)
        .filter(TicketModel.user_id == user_id)
        .order_by(TicketModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    logger.info(f"📊 [CRUD] Se encontraron {len(results)} tickets para el User ID: {user_id}")
    return results