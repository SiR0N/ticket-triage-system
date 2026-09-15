# views/history_view.py
import reflex as rx
from ticket_triage_ui.state.main_state import State

def history_tab() -> rx.Component:
    return rx.vstack(
        rx.heading("Mi Historial de Incidencias", size="5", weight="bold"),
        rx.text("Aquí puedes consultar todas las incidencias que has reportado anteriormente.", size="2", color="gray"),
        rx.cond(
            State.user_tickets.length() > 0,
            rx.vstack(
                rx.foreach(
                    State.user_tickets,
                    lambda ticket: rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.badge(f"#{ticket.get('id')}", color_scheme="gray"),
                                rx.badge(ticket.get('urgency'), color_scheme="red"),
                                rx.badge(ticket.get('department_name'), color_scheme="blue"),
                                rx.spacer(),
                                rx.text(ticket.get('created_at', ''), size="1", color="gray"),
                                width="100%",
                                align="center",
                            ),
                            rx.text(ticket.get('description', ''), size="2", weight="medium"),
                            rx.text(ticket.get('summary', ''), size="2", color="gray"),
                            spacing="2",
                            width="100%",
                        ),
                        size="2",
                        width="100%",
                    ),
                ),
                spacing="3",
                width="100%",
            ),
            rx.card(
                rx.text("No tienes ninguna incidencia registrada todavía.", size="2", color="gray"),
                width="100%",
                padding="4",
            ),
        ),
        spacing="4",
        width="100%",
    )