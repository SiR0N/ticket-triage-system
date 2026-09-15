# views/report_view.py
import reflex as rx
from ticket_triage_ui.config import PROVIDER_OPTIONS
from ticket_triage_ui.state.main_state import State


def report_tab() -> rx.Component:
    return rx.vstack(
        rx.card(
            rx.vstack(
                rx.heading("Detalles de la Incidencia", size="4", weight="bold"),
                rx.text(
                    "Escriba una descripción detallada del problema para su clasificación.",
                    size="2",
                    color_scheme="gray",
                ),
                rx.text_area(
                    placeholder="Ejemplo: La base de datos de producción presenta tiempos de espera excesivos...",
                    value=State.description,
                    on_change=State.set_description,
                    min_height="140px",
                    width="100%",
                    size="3",
                ),
                rx.cond(
                    State.user_role == "ADMIN",
                    rx.vstack(
                        rx.text("Proveedor / Modelo LLM (Solo Administradores)", size="2", weight="medium"),
                        rx.select(
                            PROVIDER_OPTIONS,
                            value=State.selected_provider,
                            on_change=State.set_selected_provider,
                            size="2",
                            width="100%",
                        ),
                        width="100%",
                    ),
                ),
                rx.button(
                    rx.hstack(rx.icon("sparkles", size=18), rx.text("Analizar y Clasificar con IA"), align="center", spacing="2"),
                    on_click=State.submit_triage,
                    loading=State.is_loading,
                    color_scheme="blue",
                    size="3",
                    width="100%",
                    cursor="pointer",
                ),
                spacing="4",
                width="100%",
            ),
            size="3",
            width="100%",
        ),
        rx.cond(
            State.has_result,
            rx.card(
                rx.vstack(
                    rx.heading("Resultado del Triaje Automático", size="4", weight="bold"),
                    rx.grid(
                        rx.card(rx.text("Categoría:"), rx.badge(State.result_category, color_scheme="purple")),
                        rx.card(rx.text("Urgencia:"), rx.badge(State.result_urgency, color_scheme="red")),
                        rx.card(rx.text("Departamento:"), rx.badge(State.result_department, color_scheme="blue")),
                        columns="3",
                        spacing="3",
                        width="100%",
                    ),
                    rx.text(State.result_summary, size="3"),
                    rx.cond(
                        State.user_role == "ADMIN",
                        rx.vstack(
                            rx.divider(margin_top="2", margin_bottom="2"),
                            rx.heading("Métricas y Análisis Técnico (Admin)", size="3", weight="bold"),
                            rx.grid(
                                rx.card(rx.text("Latencia:"), rx.badge(rx.text(State.latency, " s"), color_scheme="amber")),
                                rx.card(rx.text("Tokens consumidos:"), rx.badge(State.tokens, color_scheme="green")),
                                rx.card(rx.text("Proveedor usado:"), rx.badge(State.provider, color_scheme="cyan")),
                                columns="3",
                                spacing="3",
                                width="100%",
                            ),
                            rx.text("Proceso de pensamiento / Razonamiento:", size="2", weight="bold", margin_top="2"),
                            rx.box(
                                rx.text(State.result_thought, size="1", color="gray"),
                                padding="3",
                                background="var(--gray-3)",
                                border_radius="var(--radius-3)",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                    ),
                    spacing="4",
                    width="100%",
                ),
                size="3",
                width="100%",
            ),
        ),
        spacing="5",
        width="100%",
    )