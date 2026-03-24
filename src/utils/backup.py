import shutil
from datetime import datetime
from pathlib import Path

import config


def create_backup() -> Path:
    backup_dir = config.BASE_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = backup_dir / f"database_{timestamp}.db"
    shutil.copy2(config.DATABASE_PATH, dest)

    backups = sorted(backup_dir.glob("database_*.db"))
    for old in backups[:-10]:
        old.unlink()

    return dest
