# components/sidebar.py
import reflex as rx
from ticket_triage_ui.state.main_state import State


def sidebar() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon("bot", size=28, color="var(--accent-9)"),
            rx.heading("Triage Core", size="5", weight="bold"),
            align="center",
            spacing="2",
            margin_bottom="4",
        ),
        rx.divider(),
        rx.vstack(
            rx.hstack(
                rx.avatar(fallback=State.user_email[:2].upper(), size="3"),
                rx.vstack(
                    rx.text(State.user_email, size="2", weight="bold", truncate=True, max_width="150px"),
                    rx.badge(
                        State.user_role,
                        color_scheme=rx.cond(State.user_role == "ADMIN", "red", "blue"),
                        variant="soft",
                        size="1",
                    ),
                    spacing="1",
                    align_items="start",
                ),
                align="center",
                spacing="3",
                padding="2",
                width="100%",
                background="var(--gray-3)",
                border_radius="var(--radius-3)",
            ),
            width="100%",
        ),
        rx.text(State.user_first_name, size="2", weight="bold", truncate=True, max_width="150px"),
        rx.text(State.user_last_name, size="2", weight="bold", truncate=True, max_width="150px"),
        rx.spacer(),
        rx.button(
            rx.hstack(rx.icon("log-out", size=18), rx.text("Cerrar Sesión"), align="center", spacing="2"),
            on_click=State.logout,
            color_scheme="red",
            variant="soft",
            width="100%",
            cursor="pointer",
        ),
        padding="5",
        width="280px",
        height="100vh",
        border_right="1px solid var(--gray-4)",
        background="var(--gray-1)",
    )