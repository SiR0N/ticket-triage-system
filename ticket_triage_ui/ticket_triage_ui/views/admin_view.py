# views/admin_view.py
import reflex as rx
from ticket_triage_ui.config import DEPT_OPTIONS, URGENCY_OPTIONS
from ticket_triage_ui.state.main_state import State


def stats_tab() -> rx.Component:
    return rx.vstack(
        rx.heading("Panel de Administración y Estadísticas", size="5", weight="bold"),
        rx.text("Métricas globales del sistema y gestión centralizada de incidencias.", size="2", color="gray"),
        
        # --- TARJETAS DE ESTADÍSTICAS (KPIs) ---
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.text("Total Tickets", size="1", color="gray"),
                    rx.heading(State.total_tickets, size="6"),
                    spacing="1",
                ),
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Latencia Media", size="1", color="gray"),
                    rx.heading(rx.text(State.avg_latency, " s"), size="6"),
                    spacing="1",
                ),
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Tokens Medios", size="1", color="gray"),
                    rx.heading(State.avg_tokens, size="6"),
                    spacing="1",
                ),
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Urgencia Más Frecuente", size="1", color="gray"),
                    rx.heading(State.top_urgency, size="6"),
                    spacing="1",
                ),
                width="100%",
            ),
            columns="4",
            spacing="4",
            width="100%",
        ),
        
        rx.heading("Gestión de Todos los Tickets", size="4", weight="bold", margin_top="4"),
        
        # --- TABLA DE GESTIÓN DE TICKETS ---
        rx.card(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("ID"),
                        rx.table.column_header_cell("Descripción"),
                        rx.table.column_header_cell("Departamento"),
                        rx.table.column_header_cell("Urgencia"),
                        rx.table.column_header_cell("Acciones"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        State.tickets,
                        lambda ticket: rx.table.row(
                            rx.table.cell(rx.text(ticket["id"])),
                            rx.table.cell(rx.text(ticket["description"], truncate=True)),
                            rx.table.cell(
                                rx.select(
                                    DEPT_OPTIONS,
                                    value=State.edit_depts[ticket["id"].to_string()],
                                    on_change=lambda val: State.set_ticket_dept(ticket["id"], val),
                                    size="1",
                                    width="140px",
                                )
                            ),
                            rx.table.cell(
                                rx.select(
                                    URGENCY_OPTIONS,
                                    value=State.edit_urgencies[ticket["id"].to_string()],
                                    on_change=lambda val: State.set_ticket_urgency(ticket["id"], val),
                                    size="1",
                                    width="120px",
                                )
                            ),
                            rx.table.cell(
                                rx.button(
                                    "Guardar",
                                    size="1",
                                    color_scheme="blue",
                                    on_click=lambda: State.update_ticket(ticket["id"]),
                                    cursor="pointer",
                                )
                            ),
                        )
                    )
                ),
                width="100%",
            ),
            width="100%",
            size="3",
        ),
        
        spacing="5",
        width="100%",
    )