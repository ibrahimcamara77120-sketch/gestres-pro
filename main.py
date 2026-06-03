import sys
from PySide6.QtWidgets import QApplication, QMessageBox

from src.models.base import init_db


_TEST_ACCOUNTS = {
    "superadmin@gestres.test": ("SuperAdmin1!", "Super",  "Admin",  "super_admin", None),
    "responsable@cleanpro.test": ("Responsable1!", "Marie", "Dupont", "admin",       None),
    "employe1@cleanpro.test":    ("Employe001!",   "Karim", "Benali", "employee",    None),
    "employe2@cleanpro.test":    ("Employe002!",   "Fatou", "Diallo", "employee",    None),
    "employe3@cleanpro.test":    ("Employe003!",   "Lucas", "Martin", "employee",    None),
    "employe4@cleanpro.test":    ("Employe004!",   "Amina", "Traore", "employee",    None),
}


def _auto_seed():
    """Crée les comptes de test manquants à chaque démarrage."""
    from src.models.base import get_session
    from src.models.user import User, Role
    from src.utils.security import hash_password
    try:
        with get_session() as session:
            for email, (pwd, fn, ln, role_name, _) in _TEST_ACCOUNTS.items():
                if not session.query(User).filter_by(email=email).first():
                    role = session.query(Role).filter_by(name=role_name).first()
                    if role:
                        session.add(User(
                            email=email,
                            password_hash=hash_password(pwd),
                            first_name=fn,
                            last_name=ln,
                            role_id=role.id,
                            is_active=True,
                        ))
            session.commit()
    except Exception as e:
        print(f"[auto-seed] {e}")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GestRes Pro")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("GestRes")

    try:
        init_db()
    except Exception as e:
        QMessageBox.critical(
            None,
            "Erreur de base de données",
            f"Impossible de se connecter à la base de données.\n\n"
            f"Vérifiez que PostgreSQL est bien démarré.\n\nDétail : {e}"
        )
        sys.exit(1)

    _auto_seed()

    try:
        from src.utils.backup import create_backup
        create_backup()
    except Exception:
        pass

    try:
        from src.utils.maintenance import run_maintenance
        run_maintenance()
    except Exception:
        pass

    from src.views.styles import GLOBAL_STYLE
    from src.views.main_window import MainWindow

    app.setStyleSheet(GLOBAL_STYLE)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
