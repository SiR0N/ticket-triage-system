from typing import Any, Dict, List
import httpx
import reflex as rx
from ticket_triage_ui.config import API_URL, DEPT_OPTIONS, PROVIDER_OPTIONS, URGENCY_OPTIONS
from ticket_triage_ui.models.schemas import ProviderEnum, TicketRequest


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

    # Historial y Admin Base Data
    user_tickets: List[Dict[str, Any]] = []
    active_tab: str = "report"
    total_tickets: int = 0
    avg_latency: float = 0.0
    avg_tokens: float = 0.0
    top_urgency: str = ""
    tickets: List[Dict[str, Any]] = []
    edit_depts: Dict[str, str] = {}
    edit_urgencies: Dict[str, str] = {}

    # --- FILTRADO Y COMPARATIVA MULTI-PROVEEDOR ---
    selected_providers: List[str] = []

    def toggle_provider_filter(self, prov: str):
        """Añade o quita un proveedor de la lista de comparación."""
        if prov in self.selected_providers:
            self.selected_providers = [p for p in self.selected_providers if p != prov]
        else:
            self.selected_providers = [*self.selected_providers, prov]

    def clear_provider_filters(self):
        """Restablece el filtro para seleccionar todos los proveedores."""
        self.selected_providers = []

    # --- PROPIEDADES COMPUTADAS REACTIVAS (@rx.var) ---
    @rx.var
    def filtered_tickets(self) -> List[Dict[str, Any]]:
        """Tickets filtrados según la selección actual de proveedores."""
        if not self.selected_providers:
            return self.tickets
        return [t for t in self.tickets if str(t.get("provider", "")).lower() in [p.lower() for p in self.selected_providers]]

    @rx.var
    def stat_total_tickets(self) -> int:
        return len(self.filtered_tickets)

    @rx.var
    def stat_avg_latency(self) -> float:
        if not self.filtered_tickets:
            return 0.0
        latencies = [float(t.get("latency", 0.0)) for t in self.filtered_tickets]
        return round(sum(latencies) / len(latencies), 2)

    @rx.var
    def stat_avg_tokens(self) -> int:
        if not self.filtered_tickets:
            return 0
        tokens_list = [int(t.get("tokens_consumed", 0)) for t in self.filtered_tickets]
        return int(sum(tokens_list) / len(tokens_list))

    @rx.var
    def stat_top_urgency(self) -> str:
        if not self.filtered_tickets:
            return "N/A"
        counts: Dict[str, int] = {}
        for t in self.filtered_tickets:
            urg = str(t.get("urgency", "N/A"))
            counts[urg] = counts.get(urg, 0) + 1
        return max(counts, key=counts.get) if counts else "N/A"

    # Data para Recharts: Comparativa Latencia/Tokens por Proveedor
    @rx.var
    def chart_provider_comparison(self) -> List[Dict[str, Any]]:
        target_tickets = self.filtered_tickets
        if not target_tickets:
            return []

        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for t in target_tickets:
            p = str(t.get("provider", "desconocido")).upper()
            grouped.setdefault(p, []).append(t)

        result = []
        for prov_name, items in grouped.items():
            avg_lat = sum(float(x.get("latency", 0.0)) for x in items) / len(items)
            avg_tok = sum(int(x.get("tokens_consumed", 0)) for x in items) / len(items)
            result.append({
                "provider": prov_name,
                "latencia": round(avg_lat, 2),
                "tokens": int(avg_tok),
                "total": len(items)
            })
        return result

    # Data para Recharts: Distribución por Departamentos
    @rx.var
    def chart_department_distribution(self) -> List[Dict[str, Any]]:
        if not self.filtered_tickets:
            return []
        counts: Dict[str, int] = {}
        for t in self.filtered_tickets:
            dept = str(t.get("department_name", "Sin asignar"))
            counts[dept] = counts.get(dept, 0) + 1
        return [{"name": dept, "value": count} for dept, count in counts.items()]

    # --- CONTROLES DE PAGINACIÓN ---
    page: int = 1
    items_per_page: int = 10  # Por defecto muestra 10 tickets por página

    def next_page(self):
        if self.page < self.total_pages:
            self.page += 1

    def prev_page(self):
        if self.page > 1:
            self.page -= 1

    def set_items_per_page(self, val: str):
        self.items_per_page = int(val)
        self.page = 1

    @rx.var
    def total_pages(self) -> int:
        total = len(self.filtered_tickets)
        if total == 0:
            return 1
        return (total + self.items_per_page - 1) // self.items_per_page

    @rx.var
    def paginated_tickets(self) -> List[Dict[str, Any]]:
        """Devuelve los tickets de la página actual."""
        start = (self.page - 1) * self.items_per_page
        end = start + self.items_per_page
        return self.filtered_tickets[start:end]

    # --- MÉTODOS Y ACCIONES ---
    def set_login_username(self, val: str): self.login_username = val
    def set_login_password(self, val: str): self.login_password = val
    def set_description(self, val: str): self.description = val
    def set_selected_provider(self, val: str): self.selected_provider = val
    async def set_active_tab(self, val: str):
        """Cambia de pestaña y refresca los datos de admin si entra en la vista correspondiente."""
        self.active_tab = val
        
        # Si la pestaña activa es la de estadísticas/admin y el usuario tiene rol ADMIN, cargamos los datos frescos
        if val == "admin" and self.user_role == "ADMIN":  # Cambia "stats" por el valor exacto de la pestaña si usas otro nombre
            async for event in self.load_admin_data():
                yield event
    
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