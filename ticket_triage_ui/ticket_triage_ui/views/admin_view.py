import reflex as rx
from ticket_triage_ui.config import DEPT_OPTIONS, URGENCY_OPTIONS, PROVIDER_OPTIONS
from ticket_triage_ui.state.main_state import State


def stats_tab() -> rx.Component:
    return rx.vstack(
        # --- TITULO Y SELECCIONADOR DE PROVEEDORES ---
        rx.hstack(
            rx.vstack(
                rx.heading("Panel de Administración y Métricas de IA", size="5", weight="bold"),
                rx.text("Filtra y compara el rendimiento (latencia, tokens y volumen) entre distintos modelos de IA.", size="2", color="gray"),
                spacing="1",
            ),
            rx.spacer(),
            rx.button(
                "Ver Todos",
                size="1",
                variant="soft",
                color_scheme="gray",
                on_click=State.clear_provider_filters,
            ),
            width="100%",
            align_items="center",
        ),

        # MULTI-SELECT MEDIANTE BADGES CLICABLES
        rx.card(
            rx.hstack(
                rx.text("Comparar / Filtrar Proveedores:", size="2", weight="bold", color="gray"),
                rx.foreach(
                    PROVIDER_OPTIONS,
                    lambda prov: rx.badge(
                        prov,
                        color_scheme=rx.cond(
                            State.selected_providers.contains(prov),
                            "blue",
                            "gray"
                        ),
                        variant=rx.cond(
                            State.selected_providers.contains(prov),
                            "solid",
                            "outline"
                        ),
                        size="2",
                        cursor="pointer",
                        on_click=lambda: State.toggle_provider_filter(prov),
                    )
                ),
                spacing="2",
                align_items="center",
                wrap="wrap",
            ),
            width="100%",
            size="2",
        ),
        
        # --- TARJETAS DE ESTADÍSTICAS (KPIS DINÁMICOS) ---
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.text("Tickets (Selección)", size="1", color="gray"),
                    rx.heading(State.stat_total_tickets, size="6"),
                    spacing="1",
                ),
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Latencia Media", size="1", color="gray"),
                    rx.heading(rx.text(State.stat_avg_latency, " s"), size="6"),
                    spacing="1",
                ),
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Tokens Medios", size="1", color="gray"),
                    rx.heading(State.stat_avg_tokens, size="6"),
                    spacing="1",
                ),
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Urgencia Predominante", size="1", color="gray"),
                    rx.heading(State.stat_top_urgency, size="6"),
                    spacing="1",
                ),
                width="100%",
            ),
            columns="4",
            spacing="4",
            width="100%",
        ),

        # --- SECCIÓN DE GRÁFICOS RECHARTS ---
        rx.grid(
            # Gráfico 1: Latencia por Proveedor
            rx.card(
                rx.vstack(
                    rx.heading("Latencia Media por Proveedor (s)", size="3", weight="bold"),
                    rx.recharts.bar_chart(
                        rx.recharts.bar(data_key="latencia", fill="#3b82f6", radius=4),
                        rx.recharts.x_axis(data_key="provider"),
                        rx.recharts.y_axis(),
                        rx.recharts.tooltip(),
                        data=State.chart_provider_comparison,
                        width="100%",
                        height=200,
                    ),
                    width="100%",
                ),
                width="100%",
            ),
            # Gráfico 2: Tokens por Proveedor
            rx.card(
                rx.vstack(
                    rx.heading("Consumo Medio de Tokens por Proveedor", size="3", weight="bold"),
                    rx.recharts.bar_chart(
                        rx.recharts.bar(data_key="tokens", fill="#10b981", radius=4),
                        rx.recharts.x_axis(data_key="provider"),
                        rx.recharts.y_axis(),
                        rx.recharts.tooltip(),
                        data=State.chart_provider_comparison,
                        width="100%",
                        height=200,
                    ),
                    width="100%",
                ),
                width="100%",
            ),
            columns="2",
            spacing="4",
            width="100%",
            margin_top="2",
        ),

        # Gráfico 3: Distribución por Departamentos
        rx.card(
            rx.vstack(
                rx.heading("Volumen de Tickets por Departamento", size="3", weight="bold"),
                rx.recharts.bar_chart(
                    rx.recharts.bar(data_key="value", fill="#8b5cf6", radius=4),
                    rx.recharts.x_axis(data_key="name"),
                    rx.recharts.y_axis(),
                    rx.recharts.tooltip(),
                    data=State.chart_department_distribution,
                    width="100%",
                    height=200,
                ),
                width="100%",
            ),
            width="100%",
        ),
        
        rx.heading("Gestión de Tickets Filtrados", size="4", weight="bold", margin_top="4"),
        
        # --- TABLA DE GESTIÓN DE TICKETS PAGINADA ---
        rx.card(
            rx.vstack(
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("ID"),
                                rx.table.column_header_cell("Usuario"),
                                rx.table.column_header_cell("Descripción"),
                                rx.table.column_header_cell("Proveedor"),
                                rx.table.column_header_cell("Departamento"),
                                rx.table.column_header_cell("Urgencia"),
                                rx.table.column_header_cell("Acciones"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                State.paginated_tickets,
                                lambda ticket: rx.table.row(
                                    rx.table.cell(rx.text(ticket["id"])),
                                    rx.table.cell(rx.badge(ticket["user_email"], color_scheme="gray")),
                                    rx.table.cell(rx.text(ticket["description"], truncate=True)),
                                    rx.table.cell(rx.badge(ticket["provider"], color_scheme="purple")),
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
                    max_height="450px",
                    overflow_y="auto",
                    width="100%",
                ),
                
                # --- NAVEGACIÓN Y PAGINACIÓN DE LA TABLA ---
                rx.hstack(
                    rx.hstack(
                        rx.text("Mostrar por página:", size="1", color="gray"),
                        rx.select(
                            ["5", "10", "20", "50", "100"],
                            value=State.items_per_page.to_string(),
                            on_change=State.set_items_per_page,
                            size="1",
                            width="80px",
                        ),
                        align_items="center",
                        spacing="2",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.button(
                            "Anterior",
                            size="1",
                            variant="soft",
                            disabled=State.page <= 1,
                            on_click=State.prev_page,
                        ),
                        rx.text(
                            rx.text("Página "),
                            rx.text(State.page, weight="bold"),
                            rx.text(" de "),
                            rx.text(State.total_pages, weight="bold"),
                            size="2",
                        ),
                        rx.button(
                            "Siguiente",
                            size="1",
                            variant="soft",
                            disabled=State.page >= State.total_pages,
                            on_click=State.next_page,
                        ),
                        align_items="center",
                        spacing="3",
                    ),
                    width="100%",
                    padding_top="3",
                    border_top="1px solid var(--gray-4)",
                ),
                width="100%",
                spacing="3",
            ),
            width="100%",
            size="3",
        ),
        
        spacing="5",
        width="100%",
    )