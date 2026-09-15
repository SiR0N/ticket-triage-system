import sys
from pathlib import Path

# Añadir la raíz al path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import reflex as rx
from .components.sidebar import sidebar
from .state.main_state import State
from .views.login_view import login_view
from .views.report_view import report_tab
from .views.history_view import history_tab
from .views.admin_view import stats_tab


def dashboard_view() -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.box(
            rx.vstack(
                rx.heading("Centro de Triaje de Incidentes", size="7", weight="bold"),
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("Reportar Incidencia", value="report"),
                        rx.tabs.trigger("Mi Historial", value="history"),
                        rx.cond(State.user_role == "ADMIN", rx.tabs.trigger("Panel Admin & Stats", value="admin")),
                    ),
                    rx.tabs.content(report_tab(), value="report"),
                    rx.tabs.content(history_tab(), value="history"),
                    rx.cond(State.user_role == "ADMIN", rx.tabs.content(stats_tab(), value="admin")),
                    value=State.active_tab,
                    on_change=State.set_active_tab,
                    width="100%",
                ),
                spacing="5",
                width="100%",
            ),
            padding="8",
            width="100%",
            height="100vh",
            overflow_y="auto",
            background="var(--gray-2)",
        ),
        width="100%",
        spacing="0",
    )


def index() -> rx.Component:
    return rx.cond(State.is_authenticated, dashboard_view(), login_view())


app = rx.App()
app.add_page(index)