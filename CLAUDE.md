# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Enterprise resource management desktop application (BTS SIO project). Centralizes tracking of digital and physical resources (equipment, accounts, vehicles, access cards) with full lifecycle management, contract generation, and audit logging.

## Tech Stack

- **Language**: Python 3.14
- **GUI Framework**: PySide6 (Qt for Python)
- **Database**: PostgreSQL with SQLAlchemy ORM (driver psycopg2, URL `postgresql+psycopg2://` dans `config.py`)
- **Architecture**: MVC pattern
- **Password Hashing**: bcrypt

## Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (once requirements.txt exists)
pip install -r requirements.txt

# Run the application (once main entry point exists)
python main.py

# Run tests
python -m pytest tests/

# Run a single test file
python -m pytest tests/test_example.py -v
```

## Key Requirements

- **Security**: No raw SQL queries - use SQLAlchemy ORM exclusively. All inputs must be validated. Passwords hashed with bcrypt.
- **RGPD/CNIL Compliance**: Data minimization, configurable retention periods, anonymization for "right to be forgotten", access logging, contract integrity via hashing.
- **Database**: Foreign key constraints, automatic triggers for logging, transactions required, local backups.

## User Roles

Three-tier permission system:
1. **Super Admin** - Creates company spaces, configures resource types, defines roles
2. **Company Admin** - Full resource visibility, access to logs/history, manages internal users
3. **Employee** - Limited access based on role, digital signature, personal history
