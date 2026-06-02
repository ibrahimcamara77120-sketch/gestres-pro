from typing import List, Dict, Any, Callable, Optional, Tuple
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QFrame, QHeaderView, QComboBox,
    QSpacerItem, QSizePolicy, QAbstractItemView, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor

from src.views.styles import COLORS


class DataTable(QWidget):
    row_selected = Signal(int)
    action_triggered = Signal(str, int)
    add_clicked = Signal()
    refresh_clicked = Signal()

    def __init__(self, columns: List[Dict[str, Any]], title: str = "Données",
                 show_add_button: bool = True, show_search: bool = True,
                 page_size: int = 10, parent=None):
        super().__init__(parent)
        self._columns = columns
        self._title = title
        self._show_add_button = show_add_button
        self._show_search = show_search
        self._page_size = page_size
        self._current_page = 1
        self._total_items = 0
        self._data: List[Dict[str, Any]] = []
        self._filtered_data: List[Dict[str, Any]] = []
        self._actions: List[Dict[str, Any]] = []
        # filters: list of {"key": str, "combo": QComboBox, "type": "value"|"bool"}
        self._filters: List[Dict[str, Any]] = []
        self._filter_bar_layout: Optional[QHBoxLayout] = None
        self._container_layout: Optional[QVBoxLayout] = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['border']};
                border-radius: 14px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 18))
        container.setGraphicsEffect(shadow)

        self._container_layout = QVBoxLayout(container)
        self._container_layout.setContentsMargins(0, 0, 0, 0)
        self._container_layout.setSpacing(0)

        # ── Toolbar ──────────────────────────────────────────────
        toolbar = QFrame()
        toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-bottom: 1px solid {COLORS['border_light']};
                border-radius: 0px;
            }}
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(20, 16, 20, 16)
        toolbar_layout.setSpacing(12)

        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {COLORS['text_primary']};
            background: transparent;
        """)
        toolbar_layout.addWidget(self.title_label)
        toolbar_layout.addStretch()

        if self._show_search:
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("🔍  Rechercher...")
            self.search_input.setFixedWidth(240)
            self.search_input.setFixedHeight(36)
            self.search_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {COLORS['surface_raised']};
                    color: {COLORS['text_primary']};
                    border: 1.5px solid {COLORS['border']};
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-size: 13px;
                }}
                QLineEdit:focus {{
                    border-color: {COLORS['primary']};
                    background-color: {COLORS['white']};
                }}
            """)
            toolbar_layout.addWidget(self.search_input)

        self.refresh_button = QPushButton("↻")
        self.refresh_button.setFixedSize(36, 36)
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.setToolTip("Rafraîchir")
        self.refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface_raised']};
                color: {COLORS['text_secondary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 8px;
                font-size: 17px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['primary']};
                border-color: {COLORS['primary']};
            }}
        """)
        toolbar_layout.addWidget(self.refresh_button)

        if self._show_add_button:
            self.add_button = QPushButton("＋  Ajouter")
            self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.add_button.setFixedHeight(36)
            self.add_button.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {COLORS['primary']}, stop:1 #8b5cf6);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 0px 18px;
                    font-size: 14px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {COLORS['primary_hover']}, stop:1 #7c3aed);
                }}
            """)
            toolbar_layout.addWidget(self.add_button)

        self._container_layout.addWidget(toolbar)

        # ── Filter bar placeholder (inserted after toolbar when add_filter_bar is called) ──
        self._filter_bar_frame = None

        # ── Table ─────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(len(self._columns) + 1)

        headers = [col["label"] for col in self._columns] + ["Actions"]
        self.table.setHorizontalHeaderLabels(headers)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['white']};
                border: none;
                gridline-color: transparent;
                color: {COLORS['text_primary']};
            }}
            QTableWidget::item {{
                padding: 10px 14px;
                border-bottom: 1px solid {COLORS['border_light']};
                color: {COLORS['text_primary']};
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
                padding: 13px 14px;
                border: none;
                border-right: 1px solid {COLORS['sidebar_deep']};
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 0.6px;
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
        """)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        header = self.table.horizontalHeader()
        for i, col in enumerate(self._columns):
            if "width" in col:
                self.table.setColumnWidth(i, col["width"])
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        self.table.setColumnWidth(len(self._columns), 160)
        self._container_layout.addWidget(self.table)

        # ── Footer ─────────────────────────────────────────────────
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface_raised']};
                border-top: 1px solid {COLORS['border_light']};
                border-radius: 0px;
            }}
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 12, 20, 12)
        footer_layout.setSpacing(12)

        self.info_label = QLabel("0 élément(s)")
        self.info_label.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 13px;
            background: transparent;
        """)
        footer_layout.addWidget(self.info_label)
        footer_layout.addStretch()

        self.prev_button = QPushButton("← Précédent")
        self.prev_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_button.setStyleSheet(self._pagination_button_style())
        footer_layout.addWidget(self.prev_button)

        self.page_label = QLabel("Page 1 / 1")
        self.page_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 13px;
            font-weight: 600;
            padding: 0 12px;
            background: transparent;
        """)
        footer_layout.addWidget(self.page_label)

        self.next_button = QPushButton("Suivant →")
        self.next_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_button.setStyleSheet(self._pagination_button_style())
        footer_layout.addWidget(self.next_button)

        self._container_layout.addWidget(footer)
        layout.addWidget(container)

    # ── Filter bar ──────────────────────────────────────────────────────────
    def add_filter_bar(self):
        """Create and insert the filter bar between toolbar and table."""
        if self._filter_bar_frame is not None:
            return  # already created

        self._filter_bar_frame = QFrame()
        self._filter_bar_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface_raised']};
                border-bottom: 1px solid {COLORS['border_light']};
            }}
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 12px;
                font-weight: 600;
                background: transparent;
            }}
            QComboBox {{
                background-color: {COLORS['white']};
                color: {COLORS['text_primary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 7px;
                padding: 5px 10px;
                font-size: 13px;
                min-width: 140px;
            }}
            QComboBox:focus {{
                border-color: {COLORS['primary']};
            }}
        """)
        self._filter_bar_layout = QHBoxLayout(self._filter_bar_frame)
        self._filter_bar_layout.setContentsMargins(20, 10, 20, 10)
        self._filter_bar_layout.setSpacing(16)

        filter_icon = QLabel("⚙️  Filtres :")
        filter_icon.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; background: transparent;")
        self._filter_bar_layout.addWidget(filter_icon)

        self._filter_bar_layout.addStretch()

        # Insert at index 1 (after toolbar, before table)
        self._container_layout.insertWidget(1, self._filter_bar_frame)

    def add_filter(self, label: str, options: List[Tuple], filter_key: str,
                   filter_type: str = "value"):
        """
        Add a filter combo to the filter bar.
        options: list of (display_label, value) — value=None means "all"
        filter_type: "value" (exact match) | "bool" (True/False match)
        """
        if self._filter_bar_frame is None:
            self.add_filter_bar()

        lbl = QLabel(f"{label} :")
        self._filter_bar_layout.insertWidget(
            self._filter_bar_layout.count() - 1, lbl
        )

        combo = QComboBox()
        combo.setFixedHeight(32)
        for display, val in options:
            combo.addItem(display, val)

        combo.currentIndexChanged.connect(self._apply_all_filters)
        self._filter_bar_layout.insertWidget(
            self._filter_bar_layout.count() - 1, combo
        )

        self._filters.append({
            "key": filter_key,
            "combo": combo,
            "type": filter_type,
        })

    # ── Badge helper ─────────────────────────────────────────────────────────
    def set_status_badge(self, row_idx: int, col_idx: int,
                         text: str, text_color: str, bg_color: str):
        """Place a coloured pill badge in a table cell."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        h = QHBoxLayout(widget)
        h.setContentsMargins(6, 4, 6, 4)
        h.setSpacing(0)

        badge = QLabel(text)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 5px;
                padding: 3px 10px;
                font-size: 12px;
                font-weight: 700;
            }}
        """)
        h.addWidget(badge)
        h.addStretch()
        self.table.setCellWidget(row_idx, col_idx, widget)

    # ── Filtering logic ───────────────────────────────────────────────────────
    def _apply_all_filters(self):
        search_text = ""
        if self._show_search:
            search_text = self.search_input.text().lower()

        result = self._data

        # Text search
        if search_text:
            result = [
                row for row in result
                if any(search_text in str(row.get(col["key"], "")).lower()
                       for col in self._columns)
            ]

        # Combo filters
        for f in self._filters:
            val = f["combo"].currentData()
            if val is None:
                continue
            key = f["key"]
            if f["type"] == "bool":
                result = [row for row in result if row.get(key) == val]
            else:
                result = [row for row in result
                          if str(row.get(key, "")) == str(val)]

        self._filtered_data = result
        self._current_page = 1
        self._refresh_table()

    def _pagination_button_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {COLORS['white']};
                color: {COLORS['text_primary']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 7px;
                padding: 6px 16px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_light']};
                border-color: {COLORS['primary']};
                color: {COLORS['primary']};
            }}
            QPushButton:disabled {{
                color: {COLORS['text_muted']};
                background-color: {COLORS['border_light']};
                border-color: {COLORS['border_light']};
            }}
        """

    def _connect_signals(self):
        if self._show_search:
            self.search_input.textChanged.connect(self._apply_all_filters)

        self.refresh_button.clicked.connect(self.refresh_clicked.emit)

        if self._show_add_button:
            self.add_button.clicked.connect(self.add_clicked.emit)

        self.prev_button.clicked.connect(self._prev_page)
        self.next_button.clicked.connect(self._next_page)
        self.table.cellClicked.connect(self._on_cell_clicked)

    def set_actions(self, actions: List[Dict[str, Any]]):
        self._actions = actions

    def set_data(self, data: List[Dict[str, Any]]):
        self._data = data
        self._apply_all_filters()

    def _refresh_table(self):
        self.table.setRowCount(0)

        total = len(self._filtered_data)
        self._total_items = total
        total_pages = max(1, (total + self._page_size - 1) // self._page_size)

        start_idx = (self._current_page - 1) * self._page_size
        end_idx = min(start_idx + self._page_size, total)
        page_data = self._filtered_data[start_idx:end_idx]

        self.table.setRowCount(len(page_data))

        for row_idx, row_data in enumerate(page_data):
            for col_idx, col in enumerate(self._columns):
                key = col["key"]
                value = row_data.get(key, "")

                if "formatter" in col and col["formatter"]:
                    value = col["formatter"](value, row_data)

                # Badge rendering
                if col.get("badge") and "badge_colors" in col:
                    badge_map = col["badge_colors"]
                    str_val = str(value) if value is not None else ""
                    if str_val in badge_map:
                        tc, bc = badge_map[str_val]
                        self.set_status_badge(row_idx, col_idx, str_val, tc, bc)
                        continue

                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                if "style" in col and col["style"]:
                    style = col["style"](value, row_data)
                    if "color" in style:
                        item.setForeground(QColor(style["color"]))

                self.table.setItem(row_idx, col_idx, item)

            actions_widget = self._create_actions_widget(row_data.get("id", row_idx))
            self.table.setCellWidget(row_idx, len(self._columns), actions_widget)

        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 52)

        count_str = f"{total} élément{'s' if total != 1 else ''}"
        self.info_label.setText(count_str)
        self.page_label.setText(f"Page {self._current_page} / {total_pages}")
        self.prev_button.setEnabled(self._current_page > 1)
        self.next_button.setEnabled(self._current_page < total_pages)

    def _create_actions_widget(self, row_id: int) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        for action in self._actions:
            btn = QPushButton(action.get("icon", ""))
            btn.setToolTip(action.get("label", ""))
            btn.setFixedSize(32, 32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            color = action.get("color", COLORS['secondary'])
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color}18;
                    color: {color};
                    border: none;
                    border-radius: 7px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {color}35;
                }}
            """)

            action_name = action["name"]
            btn.clicked.connect(
                lambda checked, a=action_name, r=row_id: self.action_triggered.emit(a, r)
            )
            layout.addWidget(btn)

        layout.addStretch()
        return widget

    def _on_search(self, text: str):
        self._apply_all_filters()

    def _prev_page(self):
        if self._current_page > 1:
            self._current_page -= 1
            self._refresh_table()

    def _next_page(self):
        total_pages = max(1, (len(self._filtered_data) + self._page_size - 1) // self._page_size)
        if self._current_page < total_pages:
            self._current_page += 1
            self._refresh_table()

    def _on_cell_clicked(self, row: int, column: int):
        if column < len(self._columns):
            start_idx = (self._current_page - 1) * self._page_size
            actual_idx = start_idx + row
            if actual_idx < len(self._filtered_data):
                row_id = self._filtered_data[actual_idx].get("id", actual_idx)
                self.row_selected.emit(row_id)

    def set_title(self, title: str):
        self._title = title
        self.title_label.setText(title)

    def get_selected_id(self) -> Optional[int]:
        row = self.table.currentRow()
        if row >= 0:
            start_idx = (self._current_page - 1) * self._page_size
            actual_idx = start_idx + row
            if actual_idx < len(self._filtered_data):
                return self._filtered_data[actual_idx].get("id")
        return None
