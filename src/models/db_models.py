import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from src.database.connection import Base
from src.models.schemas import CategoryEnum, UrgencyEnum, ProviderEnum, RoleEnum


class DepartmentModel(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Relación uno-a-muchos con tickets
    tickets = relationship("TicketModel", back_populates="department")


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # 👈 Corregido 'primary_height' -> 'primary_key'
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.USER, nullable=False)  # 👈 Corregido 'Enum' -> 'SQLEnum'

    # Relación uno-a-muchos con tickets creados por el usuario
    tickets = relationship("TicketModel", back_populates="user")  # 👈 Añadida relación inversa requerida


class TicketModel(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    provider = Column(SQLEnum(ProviderEnum), nullable=False)
    
    # Datos resultantes de la clasificación
    category = Column(SQLEnum(CategoryEnum), nullable=True)
    urgency = Column(SQLEnum(UrgencyEnum), nullable=True)
    summary = Column(String, nullable=True)
    thought_process = Column(String, nullable=True)
    
    # Métricas
    latency = Column(Float, nullable=True)
    tokens_consumed = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    # --- CLAVE FORÁNEA AL DEPARTAMENTO ---
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    department = relationship("DepartmentModel", back_populates="tickets")

    # --- CLAVE FORÁNEA AL USUARIO (CREADOR) ---
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("UserModel", back_populates="tickets")