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
    app.setApplicationName("GestRes Pro")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("GestRes")

    from src.views.styles import GLOBAL_STYLE
    from src.views.main_window import MainWindow

    app.setStyleSheet(GLOBAL_STYLE)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
