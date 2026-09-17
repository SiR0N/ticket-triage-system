# config.py

from ticket_triage_ui.models.schemas import DepartmentEnum, ProviderEnum, UrgencyEnum
import os

API_URL = os.getenv("API_URL", "http://backend:8000/api/v1")

PROVIDER_OPTIONS = [p.value for p in ProviderEnum]
DEPT_OPTIONS = [d.value for d in DepartmentEnum]
URGENCY_OPTIONS = [u.value for u in UrgencyEnum]