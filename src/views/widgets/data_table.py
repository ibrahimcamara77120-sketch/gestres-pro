from typing import List, Dict, Any, Callable, Optional
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

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(16)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {COLORS['text_primary']};
            background: transparent;
        """)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        if self._show_search:
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("🔍 Rechercher...")
            self.search_input.setFixedWidth(250)
            self.search_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {COLORS['background']};
                    color: {COLORS['text_primary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 13px;
                }}
                QLineEdit:focus {{
                    border-color: {COLORS['primary']};
                }}
            """)
            header_layout.addWidget(self.search_input)

        self.refresh_button = QPushButton("↻")
        self.refresh_button.setFixedSize(36, 36)
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.setToolTip("Rafraîchir")
        self.refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['background']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
                color: {COLORS['text_primary']};
            }}
        """)
        header_layout.addWidget(self.refresh_button)

        if self._show_add_button:
            self.add_button = QPushButton("+ Ajouter")
            self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.add_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['primary']};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['primary_hover']};
                }}
            """)
            header_layout.addWidget(self.add_button)

        container_layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self._columns) + 1)

        headers = [col["label"] for col in self._columns] + ["Actions"]
        self.table.setHorizontalHeaderLabels(headers)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['white']};
                border: none;
                gridline-color: {COLORS['border_light']};
                color: {COLORS['text_primary']};
            }}
            QTableWidget::item {{
                padding: 12px 8px;
                border-bottom: 1px solid {COLORS['border_light']};
                color: {COLORS['text_primary']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['primary']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['background']};
                color: {COLORS['text_secondary']};
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid {COLORS['border']};
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
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

        self.table.setColumnWidth(len(self._columns), 150)
        container_layout.addWidget(self.table)

        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(12)

        self.info_label = QLabel("0 élément(s)")
        self.info_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
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
            color: {COLORS['text_primary']};
            font-size: 13px;
            padding: 0 12px;
            background: transparent;
        """)
        footer_layout.addWidget(self.page_label)

        self.next_button = QPushButton("Suivant →")
        self.next_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_button.setStyleSheet(self._pagination_button_style())
        footer_layout.addWidget(self.next_button)

        container_layout.addLayout(footer_layout)
        layout.addWidget(container)

    def _pagination_button_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {COLORS['white']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['background']};
                border-color: {COLORS['primary']};
            }}
            QPushButton:disabled {{
                color: {COLORS['text_muted']};
                background-color: {COLORS['border_light']};
            }}
        """

    def _connect_signals(self):
        if self._show_search:
            self.search_input.textChanged.connect(self._on_search)

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
        self._filtered_data = data.copy()
        self._current_page = 1
        self._refresh_table()

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

                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                if "style" in col and col["style"]:
                    style = col["style"](value, row_data)
                    if "color" in style:
                        item.setForeground(QColor(style["color"]))

                self.table.setItem(row_idx, col_idx, item)

            actions_widget = self._create_actions_widget(row_data.get("id", row_idx))
            self.table.setCellWidget(row_idx, len(self._columns), actions_widget)

        self.table.resizeRowsToContents()
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, max(50, self.table.rowHeight(row)))

        self.info_label.setText(f"{total} élément(s)")
        self.page_label.setText(f"Page {self._current_page} / {total_pages}")
        self.prev_button.setEnabled(self._current_page > 1)
        self.next_button.setEnabled(self._current_page < total_pages)

    def _create_actions_widget(self, row_id: int) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        for action in self._actions:
            btn = QPushButton(action.get("icon", ""))
            btn.setToolTip(action.get("label", ""))
            btn.setFixedSize(32, 32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            color = action.get("color", COLORS['secondary'])
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color}15;
                    color: {color};
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {color}30;
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
        if not text:
            self._filtered_data = self._data.copy()
        else:
            text_lower = text.lower()
            self._filtered_data = [
                row for row in self._data
                if any(text_lower in str(row.get(col["key"], "")).lower() for col in self._columns)
            ]

        self._current_page = 1
        self._refresh_table()

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
