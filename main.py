import sys
from PySide6.QtWidgets import QApplication

from src.models.base import init_db


def main():
    init_db()

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

    app = QApplication(sys.argv)
    app.setApplicationName("Gestionnaire de Ressources")
    app.setOrganizationName("BTS SIO")

    from src.views.main_window import MainWindow

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
