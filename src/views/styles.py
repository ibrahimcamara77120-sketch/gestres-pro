COLORS = {
    # Accents principaux — indigo/violet premium
    "primary":         "#6366f1",
    "primary_hover":   "#4f46e5",
    "primary_light":   "#eef2ff",
    "primary_dark":    "#3730a3",

    # Secondaires
    "secondary":       "#64748b",
    "secondary_hover": "#475569",

    # Sémantiques
    "success":        "#10b981",
    "success_light":  "#d1fae5",
    "success_dark":   "#059669",
    "warning":        "#f59e0b",
    "warning_light":  "#fef3c7",
    "warning_dark":   "#d97706",
    "danger":         "#ef4444",
    "danger_light":   "#fee2e2",
    "danger_dark":    "#dc2626",
    "info":           "#3b82f6",
    "info_light":     "#eff6ff",

    # Surfaces
    "white":          "#ffffff",
    "background":     "#f1f3fc",
    "surface":        "#ffffff",
    "surface_raised": "#f8faff",
    "border":         "#e2e8f0",
    "border_light":   "#f1f5f9",

    # Textes
    "text_primary":   "#1e1b4b",
    "text_secondary": "#64748b",
    "text_muted":     "#94a3b8",
    "text_inverse":   "#ffffff",

    # Sidebar premium
    "sidebar_bg":          "#1e1b4b",
    "sidebar_deep":        "#13113a",
    "sidebar_hover":       "#2d2a6e",
    "sidebar_active":      "#6366f1",
    "sidebar_active_glow": "#6366f140",
    "sidebar_text":        "#a5b4fc",
    "sidebar_text_active": "#ffffff",
    "sidebar_border":      "#2d2a6e",

    # Gradients stat cards
    "grad_indigo_start": "#6366f1",
    "grad_indigo_end":   "#8b5cf6",
    "grad_teal_start":   "#06b6d4",
    "grad_teal_end":     "#3b82f6",
    "grad_emerald_start":"#10b981",
    "grad_emerald_end":  "#059669",
    "grad_amber_start":  "#f59e0b",
    "grad_amber_end":    "#ef4444",
}

GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {COLORS['background']};
    color: {COLORS['text_primary']};
    font-family: "Helvetica Neue", "Arial";
    font-size: 14px;
}}

QLabel {{
    color: {COLORS['text_primary']};
    background-color: transparent;
}}

QLineEdit {{
    background-color: {COLORS['white']};
    color: {COLORS['text_primary']};
    border: 1.5px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    selection-background-color: {COLORS['primary']};
}}

QLineEdit:focus {{
    border: 2px solid {COLORS['primary']};
    background-color: {COLORS['white']};
}}

QLineEdit:disabled {{
    background-color: {COLORS['border_light']};
    color: {COLORS['text_muted']};
    border-color: {COLORS['border_light']};
}}

QLineEdit::placeholder {{
    color: {COLORS['text_muted']};
}}

QTextEdit {{
    background-color: {COLORS['white']};
    color: {COLORS['text_primary']};
    border: 1.5px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 14px;
}}

QTextEdit:focus {{
    border: 2px solid {COLORS['primary']};
}}

QDateEdit {{
    background-color: {COLORS['white']};
    color: {COLORS['text_primary']};
    border: 1.5px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 12px;
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
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_hover']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton:disabled {{
    background-color: {COLORS['border']};
    color: {COLORS['text_muted']};
}}

QComboBox {{
    background-color: {COLORS['white']};
    color: {COLORS['text_primary']};
    border: 1.5px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 14px;
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
    border-radius: 8px;
    selection-background-color: {COLORS['primary_light']};
    selection-color: {COLORS['primary']};
    padding: 6px;
}}

QTableWidget {{
    background-color: {COLORS['white']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    gridline-color: {COLORS['border_light']};
    alternate-background-color: {COLORS['surface_raised']};
}}

QTableWidget::item {{
    padding: 12px 14px;
    color: {COLORS['text_primary']};
    border: none;
}}

QTableWidget::item:selected {{
    background-color: {COLORS['primary_light']};
    color: {COLORS['primary']};
}}

QTableWidget::item:hover {{
    background-color: #f5f3ff;
}}

QHeaderView::section {{
    background-color: {COLORS['sidebar_bg']};
    color: {COLORS['sidebar_text']};
    padding: 12px 14px;
    border: none;
    border-right: 1px solid {COLORS['sidebar_deep']};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
}}

QHeaderView::section:last {{
    border-right: none;
}}

QScrollBar:vertical {{
    background-color: transparent;
    width: 6px;
    border-radius: 3px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['border']};
    border-radius: 3px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['primary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 6px;
    border-radius: 3px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['border']};
    border-radius: 3px;
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
            border-radius: 12px;
            {border_left}
        }}
    """


def primary_button_style() -> str:
    return f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: {COLORS['text_inverse']};
            border: none;
            border-radius: 8px;
            padding: 10px 22px;
            font-size: 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary_hover']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['primary_dark']};
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
            border: 1.5px solid {COLORS['border']};
            border-radius: 8px;
            padding: 10px 22px;
            font-size: 14px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary_light']};
            border-color: {COLORS['primary']};
            color: {COLORS['primary']};
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
            border-radius: 8px;
            padding: 10px 22px;
            font-size: 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {COLORS['danger_dark']};
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
            border-radius: 8px;
            padding: 10px 22px;
            font-size: 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {COLORS['success_dark']};
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
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 12px;
            font-weight: 600;
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
                border-radius: 8px;
                padding: 11px 16px;
                font-size: 13px;
                font-weight: 700;
                text-align: left;
            }}
        """
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {COLORS['sidebar_text']};
            border: none;
            border-radius: 8px;
            padding: 11px 16px;
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
            letter-spacing: 0.3px;
        }}
    """


def badge_style(color: str, bg_color: str) -> str:
    return f"""
        QLabel {{
            background-color: {bg_color};
            color: {color};
            border-radius: 4px;
            padding: 3px 9px;
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
