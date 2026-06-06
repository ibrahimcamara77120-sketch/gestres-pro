import subprocess
import os
from datetime import datetime
from pathlib import Path

import config


def create_backup() -> Path:
    backup_dir = config.BASE_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = backup_dir / f"gestres_pro_{timestamp}.sql"

    env = os.environ.copy()
    env["PGPASSWORD"] = config.DB_PASSWORD

    result = subprocess.run(
        [
            "pg_dump",
            "-h", config.DB_HOST,
            "-p", config.DB_PORT,
            "-U", config.DB_USER,
            "-d", config.DB_NAME,
            "-f", str(dest),
            "--no-password",
            "--format=plain",
        ],
        env=env,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"pg_dump échoué : {result.stderr}")

    # Garder uniquement les 10 dernières sauvegardes
    backups = sorted(backup_dir.glob("gestres_pro_*.sql"))
    for old in backups[:-10]:
        old.unlink()

    return dest