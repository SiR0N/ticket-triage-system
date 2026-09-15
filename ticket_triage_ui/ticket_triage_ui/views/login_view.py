# views/login_view.py
import reflex as rx
from ticket_triage_ui.state.main_state import State


def login_view() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("ticket", size=32, color="var(--accent-9)"),
                    rx.heading("Ticket Triage AI", size="7", weight="bold"),
                    align="center",
                    spacing="3",
                    justify="center",
                ),
                rx.text(
                    "Ingresa tus credenciales para acceder al sistema.",
                    color_scheme="gray",
                    size="2",
                    align="center",
                ),
                rx.box(height="12px"),
                rx.vstack(
                    rx.text("Usuario / Email", size="2", weight="medium"),
                    rx.input(
                        placeholder="tu.usuario@empresa.com",
                        value=State.login_username,
                        on_change=State.set_login_username,
                        size="3",
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Contraseña", size="2", weight="medium"),
                    rx.input(
                        placeholder="••••••••",
                        type="password",
                        value=State.login_password,
                        on_change=State.set_login_password,
                        size="3",
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.button(
                    rx.hstack(rx.icon("log-in", size=18), rx.text("Iniciar Sesión"), align="center", spacing="2"),
                    on_click=State.login,
                    width="100%",
                    size="3",
                    color_scheme="blue",
                    cursor="pointer",
                ),
                spacing="4",
                width="100%",
            ),
            size="4",
            max_width="420px",
            width="90%",
        ),
        height="100vh",
        background="var(--gray-2)",
    )