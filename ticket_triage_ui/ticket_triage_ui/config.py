# config.py
from src.models.schemas import DepartmentEnum, ProviderEnum, UrgencyEnum

API_URL = "http://localhost:8000/api/v1"

PROVIDER_OPTIONS = [p.value for p in ProviderEnum]
DEPT_OPTIONS = [d.value for d in DepartmentEnum]
URGENCY_OPTIONS = [u.value for u in UrgencyEnum]