# state/main_state.py
from typing import Any, Dict, List
import httpx
import reflex as rx
from ticket_triage_ui.config import API_URL, DEPT_OPTIONS, PROVIDER_OPTIONS, URGENCY_OPTIONS
from src.models.schemas import ProviderEnum, TicketRequest


class State(rx.State):
    # Auth
    token: str = ""
    user_email: str = ""
    user_role: str = ""
    login_username: str = ""
    login_password: str = ""
    is_authenticated: bool = False
    user_first_name: str = "Usuario" 
    user_last_name: str = ""         

    # Triaje Form
    description: str = ""
    selected_provider: str = PROVIDER_OPTIONS[0] if PROVIDER_OPTIONS else "GEMINI"
    is_loading: bool = False

    # Resultados
    has_result: bool = False
    result_category: str = ""
    result_urgency: str = ""
    result_department: str = ""
    result_summary: str = ""
    result_thought: str = ""
    latency: float = 0.0
    tokens: int = 0
    provider: str = ""

    # Historial y Admin
    user_tickets: List[Dict[str, Any]] = []
    active_tab: str = "report"
    total_tickets: int = 0
    avg_latency: float = 0.0
    avg_tokens: float = 0.0
    top_urgency: str = ""
    tickets: List[Dict[str, Any]] = []
    edit_depts: Dict[str, str] = {}
    edit_urgencies: Dict[str, str] = {}

    # --- MÉTODOS Y ACCIONES ---
    def set_login_username(self, val: str): self.login_username = val
    def set_login_password(self, val: str): self.login_password = val
    def set_description(self, val: str): self.description = val
    def set_selected_provider(self, val: str): self.selected_provider = val
    def set_active_tab(self, val: str): self.active_tab = val
    def set_ticket_dept(self, ticket_id: Any, val: str):
        str_id = str(ticket_id)
        self.edit_depts = {**self.edit_depts, str_id: val}

    def set_ticket_urgency(self, ticket_id: Any, val: str):
        str_id = str(ticket_id)
        self.edit_urgencies = {**self.edit_urgencies, str_id: val}

    def logout(self):
        self.reset()

    async def login(self):
        if not self.login_username or not self.login_password:
            yield rx.window_alert("⚠️ Por favor completa todos los campos.")
            return

        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(
                    f"{API_URL}/auth/login",
                    data={"username": self.login_username, "password": self.login_password},
                )
                if res.status_code == 200:
                    data = res.json()
                    self.token = data["access_token"]
                    self.user_role = data["role"]
                    self.user_email = self.login_username
                    self.is_authenticated = True
                    self.login_password = ""
                    self.user_first_name = data.get("first_name", "Usuario")
                    self.user_last_name = data.get("last_name", "")

                    async for event in self.load_user_data():
                        yield event
                    if self.user_role == "ADMIN":
                        async for event in self.load_admin_data():
                            yield event
                else:
                    yield rx.window_alert("❌ Credenciales incorrectas.")
            except Exception as e:
                yield rx.window_alert(f"🔌 Error de conexión: {e}")

    async def load_user_data(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"{API_URL}/tickets/me", headers=headers)
                if res.status_code == 200:
                    self.user_tickets = res.json()
            except Exception as e:
                yield rx.window_alert(f"Error cargando historial: {e}")

    async def submit_triage(self):
        if not self.description.strip():
            yield rx.window_alert("⚠️ Ingrese una descripción válida.")
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        selected_enum = (
            ProviderEnum(self.selected_provider)
            if self.user_role == "ADMIN"
            else getattr(ProviderEnum, "GEMINI", list(ProviderEnum)[0])
        )
        payload = TicketRequest(description=self.description, provider=selected_enum).model_dump()

        self.is_loading = True
        yield

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                res = await client.post(f"{API_URL}/triage", json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    self.result_category = data.get("category", "")
                    self.result_urgency = data.get("urgency", "")
                    self.result_department = data.get("department", "")
                    self.result_summary = data.get("summary", "")
                    self.result_thought = data.get("thought_process", "")
                    self.latency = float(data.get("latency", 0.0))
                    self.tokens = int(data.get("tokens_consumed", 0))
                    self.provider = data.get("provider", "")
                    self.has_result = True

                    async for event in self.load_user_data():
                        yield event
                else:
                    yield rx.window_alert(f"❌ Error ({res.status_code}): {res.text}")
            except Exception as e:
                yield rx.window_alert(f"Error de red: {e}")
            finally:
                self.is_loading = False

    async def load_admin_data(self):
        if self.user_role != "ADMIN":
            return
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient() as client:
            try:
                res_stats = await client.get(f"{API_URL}/stats", headers=headers)
                res_tickets = await client.get(f"{API_URL}/tickets", headers=headers)
                if res_stats.status_code == 200 and res_tickets.status_code == 200:
                    stats = res_stats.json()
                    self.tickets = res_tickets.json()
                    self.total_tickets = stats.get("total_tickets", 0)
                    self.avg_latency = float(stats.get("avg_latency", 0.0))
                    self.avg_tokens = float(stats.get("avg_tokens", 0.0))
                    self.top_urgency = stats.get("top_urgency", "N/A")
                    for t in self.tickets:
                        t_id = str(t["id"])
                        self.edit_depts[t_id] = t.get("department_name", DEPT_OPTIONS[0] if DEPT_OPTIONS else "")
                        self.edit_urgencies[t_id] = t.get("urgency", URGENCY_OPTIONS[0] if URGENCY_OPTIONS else "")
            except Exception as e:
                yield rx.window_alert(f"Error cargando estadísticas: {e}")

    async def update_ticket(self, ticket_id: Any):
        str_id = str(ticket_id)
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {}
        if str_id in self.edit_depts:
            payload["department_name"] = self.edit_depts[str_id]
        if str_id in self.edit_urgencies:
            payload["urgency"] = self.edit_urgencies[str_id]

        async with httpx.AsyncClient() as client:
            res = await client.patch(f"{API_URL}/tickets/{str_id}", json=payload, headers=headers)
            if res.status_code == 200:
                yield rx.window_alert(f"✅ Ticket #{str_id} actualizado.")
                async for event in self.load_admin_data():
                    yield event
            else:
                yield rx.window_alert(f"❌ Error al actualizar: {res.text}")