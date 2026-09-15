# components/stat_card.py
from typing import Any
import reflex as rx


def stat_card(title: str, value: Any, icon: str, color: str = "blue") -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(title, size="2", color_scheme="gray", weight="medium"),
                rx.heading(value, size="6", weight="bold"),
                align_items="start",
                spacing="1",
            ),
            rx.spacer(),
            rx.box(
                rx.icon(icon, size=24, color=f"var(--{color}-9)"),
                padding="3",
                background=f"var(--{color}-3)",
                border_radius="var(--radius-3)",
            ),
            align="center",
            width="100%",
        ),
        size="2",
        width="100%",
    )