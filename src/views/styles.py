COLORS = {
    "primary":        "#1d4ed8",
    "primary_hover":  "#1e40af",
    "primary_light":  "#dbeafe",

    "secondary":      "#475569",
    "secondary_hover":"#334155",

    "success":        "#059669",
    "success_light":  "#d1fae5",
    "warning":        "#d97706",
    "warning_light":  "#fef3c7",
    "danger":         "#dc2626",
    "danger_light":   "#fee2e2",
    "info":           "#0284c7",
    "info_light":     "#e0f2fe",

    "white":          "#ffffff",
    "background":     "#f1f5f9",
    "surface":        "#ffffff",
    "border":         "#cbd5e1",
    "border_light":   "#e2e8f0",

    "text_primary":   "#0f172a",
    "text_secondary": "#475569",
    "text_muted":     "#94a3b8",
    "text_inverse":   "#ffffff",

    "sidebar_bg":     "#0f172a",
    "sidebar_hover":  "#1e293b",
    "sidebar_active": "#1d4ed8",
    "sidebar_text":   "#94a3b8",
    "sidebar_text_active": "#ffffff",
}

GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {COLORS['background']};
    color: {COLORS['text_primary']};
    font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 14px;
}}

QLabel {{
    color: {COLORS['text_primary']};
    background-color: transparent;
}}

QLineEdit {{
    background-color: {COLORS['white']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 5px;
    padding: 9px 12px;
    font-size: 14px;
    selection-background-color: {COLORS['primary']};
}}

QLineEdit:focus {{
    border: 2px solid {COLORS['primary']};
    padding: 8px 11px;
}}

QLineEdit:disabled {{
    background-color: {COLORS['border_light']};
    color: {COLORS['text_muted']};
}}

QLineEdit::placeholder {{
    color: {COLORS['text_muted']};
}}

QTextEdit {{
    background-color: {COLORS['white']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 5px;
    padding: 8px 10px;
    font-size: 14px;
    selection-background-color: {COLORS['primary']};
}}

QTextEdit:focus {{
    border: 2px solid {COLORS['primary']};
}}

QDateEdit {{
    background-color: {COLORS['white']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 5px;
    padding: 8px 12px;
    font-size: 14px;
}}

QDateEdit:focus {{
    border: 2px solid {COLORS['primary']};
}}

QDateEdit::drop-down {{
    border: none;
    padding-right: 8px;
}}

QPushButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_inverse']};
    border: none;
    border-radius: 5px;
    padding: 9px 18px;
    font-size: 14px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_hover']};
}}

QPushButton:pressed {{
    background-color: #1e3a8a;
}}

QPushButton:disabled {{
    background-color: {COLORS['border']};
    color: {COLORS['text_muted']};
}}

QComboBox {{
    background-color: {COLORS['white']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 5px;
    padding: 9px 12px;
    font-size: 14px;
}}

QComboBox:focus {{
    border: 2px solid {COLORS['primary']};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['white']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    selection-background-color: {COLORS['primary_light']};
    selection-color: {COLORS['primary']};
    padding: 4px;
}}

QTableWidget {{
    background-color: {COLORS['white']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    gridline-color: {COLORS['border_light']};
    alternate-background-color: {COLORS['background']};
}}

QTableWidget::item {{
    padding: 10px 12px;
    color: {COLORS['text_primary']};
    border: none;
}}

QTableWidget::item:selected {{
    background-color: {COLORS['primary_light']};
    color: {COLORS['primary']};
}}

QTableWidget::item:hover {{
    background-color: {COLORS['border_light']};
}}

QHeaderView::section {{
    background-color: {COLORS['sidebar_hover']};
    color: {COLORS['text_inverse']};
    padding: 10px 12px;
    border: none;
    border-right: 1px solid {COLORS['sidebar_bg']};
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QHeaderView::section:last {{
    border-right: none;
}}

QScrollBar:vertical {{
    background-color: {COLORS['border_light']};
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['border']};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['secondary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {COLORS['border_light']};
    height: 8px;
    border-radius: 4px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['border']};
    border-radius: 4px;
    min-width: 30px;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

QMessageBox {{
    background-color: {COLORS['white']};
}}

QMessageBox QLabel {{
    color: {COLORS['text_primary']};
    font-size: 14px;
}}

QInputDialog {{
    background-color: {COLORS['white']};
}}

QInputDialog QLabel {{
    color: {COLORS['text_primary']};
}}

QInputDialog QLineEdit {{
    color: {COLORS['text_primary']};
}}

QDialog {{
    background-color: {COLORS['white']};
}}
"""


def card_style(accent_color: str = None) -> str:
    border_left = f"border-left: 4px solid {accent_color};" if accent_color else ""
    return f"""
        QFrame {{
            background-color: {COLORS['white']};
            border: 1px solid {COLORS['border']};
            border-radius: 6px;
            {border_left}
        }}
    """


def primary_button_style() -> str:
    return f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: {COLORS['text_inverse']};
            border: none;
            border-radius: 5px;
            padding: 10px 22px;
            font-size: 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary_hover']};
        }}
        QPushButton:pressed {{
            background-color: #1e3a8a;
        }}
        QPushButton:disabled {{
            background-color: {COLORS['border']};
            color: {COLORS['text_muted']};
        }}
    """


def secondary_button_style() -> str:
    return f"""
        QPushButton {{
            background-color: {COLORS['white']};
            color: {COLORS['text_primary']};
            border: 1px solid {COLORS['border']};
            border-radius: 5px;
            padding: 10px 22px;
            font-size: 14px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {COLORS['border_light']};
            border-color: {COLORS['secondary']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['border']};
        }}
    """


def danger_button_style() -> str:
    return f"""
        QPushButton {{
            background-color: {COLORS['danger']};
            color: {COLORS['text_inverse']};
            border: none;
            border-radius: 5px;
            padding: 10px 22px;
            font-size: 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: #b91c1c;
        }}
        QPushButton:pressed {{
            background-color: #991b1b;
        }}
    """


def success_button_style() -> str:
    return f"""
        QPushButton {{
            background-color: {COLORS['success']};
            color: {COLORS['text_inverse']};
            border: none;
            border-radius: 5px;
            padding: 10px 22px;
            font-size: 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: #047857;
        }}
        QPushButton:pressed {{
            background-color: #065f46;
        }}
    """


def action_button_style(color: str) -> str:
    hover_color = _darken_color(color, 0.85)
    return f"""
        QPushButton {{
            background-color: {color};
            color: {COLORS['text_inverse']};
            border: none;
            border-radius: 4px;
            padding: 6px 14px;
            font-size: 12px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
    """


SIDEBAR_STYLE = f"""
    QFrame {{
        background-color: {COLORS['sidebar_bg']};
        border: none;
    }}
"""


def sidebar_button_style(is_active: bool = False) -> str:
    if is_active:
        return f"""
            QPushButton {{
                background-color: {COLORS['sidebar_active']};
                color: {COLORS['sidebar_text_active']};
                border: none;
                border-radius: 5px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 600;
                text-align: left;
            }}
        """
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS['sidebar_text']};
            border: none;
            border-radius: 5px;
            padding: 10px 16px;
            font-size: 13px;
            font-weight: 400;
            text-align: left;
        }}
        QPushButton:hover {{
            background-color: {COLORS['sidebar_hover']};
            color: {COLORS['sidebar_text_active']};
        }}
    """


def input_group_style() -> str:
    return f"""
        QLabel {{
            color: {COLORS['text_secondary']};
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 3px;
            background-color: transparent;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
    """


def badge_style(color: str, bg_color: str) -> str:
    return f"""
        QLabel {{
            background-color: {bg_color};
            color: {color};
            border-radius: 3px;
            padding: 3px 8px;
            font-size: 11px;
            font-weight: 700;
        }}
    """


def _darken_color(hex_color: str, factor: float = 0.85) -> str:
    color = hex_color.lstrip('#')
    r, g, b = int(color[:2], 16), int(color[2:4], 16), int(color[4:], 16)
    r = max(0, int(r * factor))
    g = max(0, int(g * factor))
    b = max(0, int(b * factor))
    return f"#{r:02x}{g:02x}{b:02x}"
