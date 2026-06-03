from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QScrollArea,
    QSizePolicy, QGraphicsDropShadowEffect, QStackedWidget, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QColor, QPainter, QLinearGradient, QBrush

from src.controllers.auth_controller import auth_controller
from src.views.styles import COLORS


class StatCard(QFrame):
    """Carte statistique avec fond dégradé coloré."""

    def __init__(self, title: str, value: str, icon: str,
                 grad_start: str, grad_end: str, parent=None):
        super().__init__(parent)
        self._grad_start = grad_start
        self._grad_end = grad_end
        self._setup_ui(title, value, icon, grad_start, grad_end)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(self._grad_start))
        gradient.setColorAt(1.0, QColor(self._grad_end))
        from PySide6.QtGui import QPainterPath
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 14, 14)
        painter.fillPath(path, QBrush(gradient))

    def _setup_ui(self, title: str, value: str, icon: str,
                  grad_start: str, grad_end: str):
        self.setMinimumSize(220, 130)
        self.setMaximumHeight(130)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("QFrame { border: none; border-radius: 14px; }")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(grad_start.replace("#", "") and QColor(grad_start)))
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(6)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            color: rgba(255,255,255,0.80);
            font-size: 12px;
            font-weight: 600;
            background: transparent;
            letter-spacing: 0.5px;
        """)
        text_layout.addWidget(self.title_label)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("""
            color: white;
            font-size: 36px;
            font-weight: 800;
            background: transparent;
        """)
        text_layout.addWidget(self.value_label)

        text_layout.addStretch()
        layout.addLayout(text_layout)
        layout.addStretch()

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("""
            font-size: 44px;
            background: transparent;
            color: rgba(255,255,255,0.35);
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

    def set_value(self, value: str):
        self.value_label.setText(value)


class QuickActionCard(QFrame):
    clicked = Signal()

    def __init__(self, title: str, description: str, icon: str, color: str, parent=None):
        super().__init__(parent)
        self._setup_ui(title, description, icon, color)

    def _setup_ui(self, title: str, description: str, icon: str, color: str):
        self.setMinimumHeight(100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border: 1.5px solid {COLORS['border']};
                border-radius: 14px;
            }}
            QFrame:hover {{
                border-color: {color};
                background-color: #faf9ff;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        icon_container = QFrame()
        icon_container.setFixedSize(50, 50)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background-color: {color}20;
                border-radius: 25px;
                border: none;
            }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 24px; background: transparent;")
        icon_layout.addWidget(icon_label)
        layout.addWidget(icon_container)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 15px;
            font-weight: 600;
            background: transparent;
        """)
        text_layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 13px;
            background: transparent;
        """)
        text_layout.addWidget(desc_label)

        layout.addLayout(text_layout)
        layout.addStretch()

        arrow = QLabel("→")
        arrow.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 20px; background: transparent;")
        layout.addWidget(arrow)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class DashboardView(QWidget):
    logout_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.setStyleSheet(f"background-color: {COLORS['background']};")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet(f"QFrame {{ background-color: {COLORS['sidebar_bg']}; border: none; }}")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 20, 16, 20)
        sidebar_layout.setSpacing(8)

        logo_container = QHBoxLayout()
        logo_badge = QLabel("GR")
        logo_badge.setFixedSize(40, 40)
        logo_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_badge.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS['primary']}, stop:1 #8b5cf6);
            color: white;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 800;
        """)
        logo_container.addWidget(logo_badge)
        logo_container.addSpacing(12)

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        app_title = QLabel("GestRes Pro")
        app_title.setStyleSheet(f"color: {COLORS['white']}; font-size: 16px; font-weight: 800; background: transparent;")
        app_sub = QLabel("Gestion de ressources")
        app_sub.setStyleSheet(f"color: {COLORS['sidebar_text']}; font-size: 10px; background: transparent;")
        title_col.addWidget(app_title)
        title_col.addWidget(app_sub)
        logo_container.addLayout(title_col)
        logo_container.addStretch()
        sidebar_layout.addLayout(logo_container)

        # Séparateur
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COLORS['sidebar_border']}; margin: 4px 0px;")
        sidebar_layout.addWidget(sep)

        sidebar_layout.addSpacing(30)

        menu_label = QLabel("MENU PRINCIPAL")
        menu_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; font-weight: 600; letter-spacing: 1px; background: transparent; margin-bottom: 8px;")
        sidebar_layout.addWidget(menu_label)

        self.btn_dashboard  = self._create_menu_button("🏠  Tableau de bord", True)
        self.btn_users      = self._create_menu_button("👥  Utilisateurs", False)
        self.btn_companies  = self._create_menu_button("🏢  Entreprises", False)
        self.btn_resources  = self._create_menu_button("🖥️  Ressources", False)
        self.btn_assignments = self._create_menu_button("📋  Affectations", False)
        self.btn_contracts  = self._create_menu_button("📄  Contrats", False)

        for btn in [self.btn_dashboard, self.btn_users, self.btn_companies,
                    self.btn_resources, self.btn_assignments, self.btn_contracts]:
            sidebar_layout.addWidget(btn)

        sidebar_layout.addSpacing(20)

        self.admin_label = QLabel("ADMINISTRATION")
        self.admin_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; font-weight: 600; letter-spacing: 1px; background: transparent; margin-bottom: 8px;")
        sidebar_layout.addWidget(self.admin_label)

        self.btn_logs = self._create_menu_button("📊  Journaux d'audit", False)
        sidebar_layout.addWidget(self.btn_logs)

        sidebar_layout.addStretch()

        user_frame = QFrame()
        user_frame.setStyleSheet(f"QFrame {{ background-color: {COLORS['sidebar_hover']}; border-radius: 10px; border: none; }}")
        user_layout = QHBoxLayout(user_frame)
        user_layout.setContentsMargins(12, 12, 12, 12)

        user_avatar = QLabel("U")
        user_avatar.setFixedSize(34, 34)
        user_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_avatar.setStyleSheet(f"""
            background-color: {COLORS['secondary']};
            color: white;
            border-radius: 17px;
            font-size: 13px;
            font-weight: bold;
        """)
        user_layout.addWidget(user_avatar)

        user_info = QVBoxLayout()
        user_info.setSpacing(2)

        self.user_name_label = QLabel("Utilisateur")
        self.user_name_label.setStyleSheet(f"color: {COLORS['white']}; font-size: 14px; font-weight: 600; background: transparent;")
        user_info.addWidget(self.user_name_label)

        self.user_role_label = QLabel("Rôle")
        self.user_role_label.setStyleSheet(f"color: {COLORS['sidebar_text']}; font-size: 12px; background: transparent;")
        user_info.addWidget(self.user_role_label)

        user_layout.addLayout(user_info)

        sidebar_layout.addWidget(user_frame)

        self.logout_button = QPushButton("⏻  Se déconnecter")
        self.logout_button.setMinimumHeight(42)
        self.logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']}18;
                color: {COLORS['danger']};
                border: 1.5px solid {COLORS['danger']}40;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                padding: 0px 16px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger']};
                color: white;
                border-color: {COLORS['danger']};
            }}
        """)
        sidebar_layout.addWidget(self.logout_button)

        main_layout.addWidget(sidebar)

        main_layout.addWidget(sidebar)

        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"background-color: {COLORS['background']};")

        self._home_page = self._build_home_page()
        self.content_stack.addWidget(self._home_page)

        # pages créées à la demande
        self._pages = {}

        main_layout.addWidget(self.content_stack)

    def _build_home_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background-color: {COLORS['background']}; }}")

        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {COLORS['background']};")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)

        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()

        self.welcome_label = QLabel("Bonjour,")
        self.welcome_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 32px;
            font-weight: 800;
            background: transparent;
            letter-spacing: -0.5px;
        """)
        header_text.addWidget(self.welcome_label)

        self.date_label = QLabel("Voici un aperçu de votre activité")
        self.date_label.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 15px;
            background: transparent;
            margin-top: 2px;
        """)
        header_text.addWidget(self.date_label)

        header_layout.addLayout(header_text)
        header_layout.addStretch()
        content_layout.addLayout(header_layout)

        stats_title = QLabel("📊  Vue d'ensemble")
        stats_title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 17px;
            font-weight: 700;
            background: transparent;
        """)
        content_layout.addWidget(stats_title)

        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(20)

        self.users_card = StatCard("Utilisateurs actifs", "0", "👥",
                                   COLORS['grad_indigo_start'], COLORS['grad_indigo_end'])
        self.stats_grid.addWidget(self.users_card, 0, 0)
        self.resources_card = StatCard("Ressources totales", "0", "🖥",
                                       COLORS['grad_teal_start'], COLORS['grad_teal_end'])
        self.stats_grid.addWidget(self.resources_card, 0, 1)
        self.assignments_card = StatCard("Affectations actives", "0", "📋",
                                         COLORS['grad_emerald_start'], COLORS['grad_emerald_end'])
        self.stats_grid.addWidget(self.assignments_card, 0, 2)
        self.companies_card = StatCard("Entreprises", "0", "🏢",
                                       COLORS['grad_amber_start'], COLORS['grad_amber_end'])
        self.stats_grid.addWidget(self.companies_card, 0, 3)

        content_layout.addLayout(self.stats_grid)

        actions_title = QLabel("⚡  Actions rapides")
        actions_title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 17px;
            font-weight: 700;
            background: transparent;
            margin-top: 10px;
        """)
        content_layout.addWidget(actions_title)

        self.actions_grid = QGridLayout()
        self.actions_grid.setSpacing(14)

        self.action_new_user = QuickActionCard(
            "Nouvel utilisateur", "Créer un compte utilisateur", "👤", COLORS['primary'])
        self.actions_grid.addWidget(self.action_new_user, 0, 0)
        self.action_new_resource = QuickActionCard(
            "Nouvelle ressource", "Ajouter une ressource au parc", "🖥️", COLORS['success'])
        self.actions_grid.addWidget(self.action_new_resource, 0, 1)
        self.action_new_assignment = QuickActionCard(
            "Nouvelle affectation", "Affecter une ressource à un employé", "📋", COLORS['warning'])
        self.actions_grid.addWidget(self.action_new_assignment, 1, 0)
        self.action_view_logs = QuickActionCard(
            "Journaux d'audit", "Consulter l'historique des actions", "📊", COLORS['secondary'])
        self.actions_grid.addWidget(self.action_view_logs, 1, 1)

        content_layout.addLayout(self.actions_grid)
        content_layout.addStretch()

        scroll.setWidget(content_widget)
        return scroll

    def _create_menu_button(self, text: str, is_active: bool) -> QPushButton:
        btn = QPushButton(f"  {text}")
        btn.setMinimumHeight(40)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(self._menu_btn_style(is_active))
        return btn

    def _menu_btn_style(self, is_active: bool) -> str:
        if is_active:
            return f"""
                QPushButton {{
                    background-color: {COLORS['sidebar_active']};
                    color: {COLORS['white']};
                    border: none;
                    border-left: 3px solid #a5b4fc;
                    border-radius: 8px;
                    padding: 11px 16px;
                    font-size: 14px;
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
                font-size: 14px;
                font-weight: 400;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {COLORS['sidebar_hover']};
                color: {COLORS['white']};
            }}
        """

    def _connect_signals(self):
        self.logout_button.clicked.connect(self._on_logout_clicked)

        self.btn_dashboard.clicked.connect(lambda: self._navigate("home"))
        self.btn_users.clicked.connect(lambda: self._navigate("users"))
        self.btn_companies.clicked.connect(lambda: self._navigate("companies"))
        self.btn_resources.clicked.connect(lambda: self._navigate("resources"))
        self.btn_assignments.clicked.connect(lambda: self._navigate("assignments"))
        self.btn_contracts.clicked.connect(lambda: self._navigate("contracts"))
        self.btn_logs.clicked.connect(lambda: self._navigate("logs"))

        self.action_new_user.clicked.connect(lambda: self._navigate("users"))
        self.action_new_resource.clicked.connect(lambda: self._navigate("resources"))
        self.action_new_assignment.clicked.connect(lambda: self._navigate("assignments"))
        self.action_view_logs.clicked.connect(lambda: self._navigate("logs"))

    def _navigate(self, page: str):
        self._set_active_button(page)

        if page == "home":
            self.content_stack.setCurrentWidget(self._home_page)
            return

        if page not in self._pages:
            self._pages[page] = self._create_page(page)
            if self._pages[page]:
                self.content_stack.addWidget(self._pages[page])

        if page in self._pages and self._pages[page]:
            widget = self._pages[page]
            self.content_stack.setCurrentWidget(widget)
            if hasattr(widget, "load_data"):
                widget.load_data()

    def _create_page(self, page: str):
        try:
            if page == "users":
                from src.views.users_view import UsersView
                return UsersView()
            elif page == "companies":
                from src.views.companies_view import CompaniesView
                return CompaniesView()
            elif page == "resources":
                from src.views.resources_view import ResourcesView
                return ResourcesView()
            elif page == "assignments":
                from src.views.assignments_view import AssignmentsView
                return AssignmentsView()
            elif page == "contracts":
                from src.views.contracts_view import ContractsView
                return ContractsView()
            elif page == "logs":
                from src.views.logs_view import LogsView
                return LogsView()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger la page : {e}")
            return None

    def _set_active_button(self, page: str):
        mapping = {
            "home": self.btn_dashboard,
            "users": self.btn_users,
            "companies": self.btn_companies,
            "resources": self.btn_resources,
            "assignments": self.btn_assignments,
            "contracts": self.btn_contracts,
            "logs": self.btn_logs,
        }
        for p, btn in mapping.items():
            btn.setStyleSheet(self._menu_btn_style(p == page))

    def _on_logout_clicked(self):
        reply = QMessageBox.question(self, "Déconnexion", "Voulez-vous vraiment vous déconnecter ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()

    def refresh(self):
        user = auth_controller.current_user
        if not user:
            return

        self.user_name_label.setText(user.full_name)
        role_display = {"super_admin": "Super Administrateur", "admin": "Administrateur", "employee": "Employé"}
        self.user_role_label.setText(role_display.get(user.role.name, user.role.name))
        self.welcome_label.setText(f"Bonjour, {user.first_name or 'Utilisateur'} 👋")

        from datetime import date
        DAYS = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]
        MONTHS = ["janvier","février","mars","avril","mai","juin",
                  "juillet","août","septembre","octobre","novembre","décembre"]
        today = date.today()
        date_str = f"{DAYS[today.weekday()]} {today.day} {MONTHS[today.month - 1]} {today.year}"
        self.date_label.setText(f"Bienvenue sur GestRes Pro  ·  {date_str}")

        is_admin = auth_controller.is_admin()
        is_super = auth_controller.is_super_admin()

        self.btn_users.setVisible(is_admin)
        self.btn_companies.setVisible(is_super)
        self.btn_logs.setVisible(is_admin)
        self.admin_label.setVisible(is_admin)
        self.action_new_user.setVisible(is_admin)
        self.action_view_logs.setVisible(is_admin)
        self.users_card.setVisible(is_admin)
        self.companies_card.setVisible(is_admin)

        if not is_admin:
            # Cartes stats : aligner "Ressources" et "Affectations" côte à côte
            self.stats_grid.removeWidget(self.resources_card)
            self.stats_grid.removeWidget(self.assignments_card)
            self.stats_grid.addWidget(self.resources_card,   0, 0)
            self.stats_grid.addWidget(self.assignments_card, 0, 1)

            # Actions rapides : aligner les 2 cartes côte à côte
            self.actions_grid.removeWidget(self.action_new_resource)
            self.actions_grid.removeWidget(self.action_new_assignment)
            self.actions_grid.addWidget(self.action_new_resource,   0, 0)
            self.actions_grid.addWidget(self.action_new_assignment, 0, 1)

        self._pages = {}
        self._navigate("home")
        self._load_statistics()

    def _load_statistics(self):
        try:
            from src.models.base import get_session
            from src.models.user import User
            from src.models.company import Company
            from src.models.resource import Resource
            from src.models.assignment import Assignment

            is_admin = auth_controller.is_admin()
            user = auth_controller.current_user

            with get_session() as session:
                if is_admin:
                    self.users_card.set_value(str(session.query(User).filter_by(is_active=True).count()))
                    self.resources_card.set_value(str(session.query(Resource).count()))
                    self.assignments_card.set_value(str(session.query(Assignment).filter_by(status="active").count()))
                    self.companies_card.set_value(str(session.query(Company).filter_by(is_active=True).count()))
                else:
                    uid = user.id if user else None
                    my_assignments = session.query(Assignment).filter_by(user_id=uid, status="active").count()
                    my_resources = session.query(Assignment).filter_by(user_id=uid, status="active").count()
                    self.resources_card.set_value(str(my_resources))
                    self.assignments_card.set_value(str(my_assignments))
                    self.resources_card.title_label.setText("Mes ressources")
                    self.assignments_card.title_label.setText("Mes affectations")
        except Exception:
            pass
