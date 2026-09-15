import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Asegurar que la carpeta 'data/' exista para no saturar la raíz del proyecto
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 2. Ruta a la base de datos dentro de /data
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'incidencias.db')}"

# 3. Motor y Sesión de SQLAlchemy
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Declarative Base (Sintaxis moderna)
Base = declarative_base()


def seed_departments(db):
    """Inserta los departamentos base si la tabla está vacía."""
    from src.models.db_models import DepartmentModel
    from src.models.schemas import DepartmentEnum

    if db.query(DepartmentModel).count() == 0:
        departments_data = [
            DepartmentModel(code=dept.name, name=dept.value)
            for dept in DepartmentEnum
        ]
        db.add_all(departments_data)
        db.commit()


def seed_users(db):
    """Crea un usuario normal y un administrador por defecto si la tabla está vacía."""
    from src.models.db_models import UserModel
    from src.models.schemas import RoleEnum
    from src.core.security import hash_password

    if db.query(UserModel).count() == 0:
        default_users = [
            UserModel(
                email="admin@empresa.com",
                first_name="Admin",
                last_name="Sistemas",
                hashed_password=hash_password("admin123"),
                role=RoleEnum.ADMIN
            ),
            UserModel(
                email="user@empresa.com",
                first_name="Juan",
                last_name="Pérez Gómez",
                hashed_password=hash_password("user123"),
                role=RoleEnum.USER
            ),
        ]
        db.add_all(default_users)
        db.commit()


def init_db():
    import src.models.db_models  # Cargar modelos en la metadata
    Base.metadata.create_all(bind=engine)
    
    # Poblar las tablas tras crear la BD
    db = SessionLocal()
    try:
        seed_departments(db)
        seed_users(db)  # 👈 Insertar usuarios predefinidos
    finally:
        db.close()


# 5. Generador de sesiones para inyección de dependencias en FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()