"""
db.py — VAST SE Toolkit project database
SQLite-backed project persistence with versioning and backup.

Database location (inside container): /app/data/toolkit.db
Host location (via volume mount):     ~/projects/vast-se-toolkit/data/toolkit.db
"""

import sqlite3
import json
import shutil
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

APP_VERSION = "1.0.0"
DB_PATH = Path(os.environ.get("TOOLKIT_DB_PATH", "/app/data/toolkit.db"))

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    cluster         TEXT    NOT NULL,
    customer        TEXT    NOT NULL,
    created_at      TEXT    NOT NULL,
    updated_at      TEXT    NOT NULL,
    app_version     TEXT    NOT NULL,
    is_deleted      INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS project_versions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      INTEGER NOT NULL REFERENCES projects(id),
    version_num     INTEGER NOT NULL,
    saved_at        TEXT    NOT NULL,
    app_version     TEXT    NOT NULL,
    label           TEXT,
    state_json      TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key             TEXT    PRIMARY KEY,
    value           TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pv_project ON project_versions(project_id);
"""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _init_db():
    with _connect() as conn:
        conn.executescript(SCHEMA)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _state_to_json(session_state: dict) -> str:
    """
    Serialise session_state to JSON.
    Drops non-serialisable Streamlit internals silently.
    """
    safe = {}
    for k, v in session_state.items():
        if k.startswith("_") or k.startswith("FormSubmitter"):
            continue
        try:
            json.dumps(v)
            safe[k] = v
        except (TypeError, ValueError):
            pass
    return json.dumps(safe, indent=2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def save_project(session_state: dict, label: str = None) -> int:
    """
    Save a full state snapshot.
    Creates a new project row on first save (no id in session_state),
    otherwise updates the existing project and appends a version row.

    Returns the project_id.
    """
    _init_db()
    now = _now()
    state_json = _state_to_json(session_state)

    cluster  = session_state.get("cluster_name", "unknown")
    customer = session_state.get("customer", "unknown")
    name     = session_state.get("project_name") or f"{customer} — {cluster}"

    project_id = session_state.get("_db_project_id")

    with _connect() as conn:
        if project_id is None:
            cur = conn.execute(
                """INSERT INTO projects
                   (name, cluster, customer, created_at, updated_at, app_version)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (name, cluster, customer, now, now, APP_VERSION),
            )
            project_id = cur.lastrowid
            log.info("Created project id=%s", project_id)
        else:
            conn.execute(
                """UPDATE projects
                   SET name=?, cluster=?, customer=?, updated_at=?, app_version=?
                   WHERE id=?""",
                (name, cluster, customer, now, APP_VERSION, project_id),
            )

        # Version number = count of existing versions + 1
        row = conn.execute(
            "SELECT COALESCE(MAX(version_num), 0) FROM project_versions WHERE project_id=?",
            (project_id,),
        ).fetchone()
        next_version = row[0] + 1

        conn.execute(
            """INSERT INTO project_versions
               (project_id, version_num, saved_at, app_version, label, state_json)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (project_id, next_version, now, APP_VERSION, label, state_json),
        )

    return project_id


def load_project(project_id: int) -> dict:
    """
    Load the latest state snapshot for a project.
    Returns a dict that can be merged into session_state.
    """
    _init_db()
    with _connect() as conn:
        row = conn.execute(
            """SELECT state_json FROM project_versions
               WHERE project_id=?
               ORDER BY version_num DESC LIMIT 1""",
            (project_id,),
        ).fetchone()
    if row is None:
        raise ValueError(f"No versions found for project_id={project_id}")
    state = json.loads(row["state_json"])
    state["_db_project_id"] = project_id
    return state


def load_version(version_id: int) -> dict:
    """Load a specific version row by its primary key id."""
    _init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT state_json, project_id FROM project_versions WHERE id=?",
            (version_id,),
        ).fetchone()
    if row is None:
        raise ValueError(f"Version id={version_id} not found")
    state = json.loads(row["state_json"])
    state["_db_project_id"] = row["project_id"]
    return state


def list_projects() -> list[dict]:
    """
    Return all non-deleted projects, most recently updated first.
    Each dict has: id, name, cluster, customer, created_at, updated_at, app_version.
    """
    _init_db()
    with _connect() as conn:
        rows = conn.execute(
            """SELECT id, name, cluster, customer, created_at, updated_at, app_version
               FROM projects
               WHERE is_deleted=0
               ORDER BY updated_at DESC""",
        ).fetchall()
    return [dict(r) for r in rows]


def delete_project(project_id: int):
    """Soft-delete a project (sets is_deleted=1)."""
    _init_db()
    with _connect() as conn:
        conn.execute(
            "UPDATE projects SET is_deleted=1 WHERE id=?", (project_id,)
        )


def delete_version(version_id: int):
    """Hard-delete a single version snapshot."""
    _init_db()
    with _connect() as conn:
        conn.execute("DELETE FROM project_versions WHERE id=?", (version_id,))


def get_project_versions(project_id: int) -> list[dict]:
    """
    Return all version snapshots for a project, newest first.
    Each dict has: id, version_num, saved_at, app_version, label.
    """
    _init_db()
    with _connect() as conn:
        rows = conn.execute(
            """SELECT id, version_num, saved_at, app_version, label
               FROM project_versions
               WHERE project_id=?
               ORDER BY version_num DESC""",
            (project_id,),
        ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

def get_setting(key: str, default: str = None) -> Optional[str]:
    _init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT value FROM settings WHERE key=?", (key,)
        ).fetchone()
    return row["value"] if row else default


def set_setting(key: str, value: str):
    _init_db()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO settings(key, value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )


def get_backup_location() -> str:
    """Return configured backup directory, defaulting to user home."""
    return get_setting("backup_location", str(Path.home() / "vast-toolkit-backups"))


def set_backup_location(path: str):
    set_setting("backup_location", path)


# ---------------------------------------------------------------------------
# Backup / Restore / Export
# ---------------------------------------------------------------------------

def backup(destination_path: str = None) -> str:
    """
    Copy toolkit.db to destination_path (directory or full filepath).
    Returns the path of the backup file created.
    """
    _init_db()
    dest = Path(destination_path or get_backup_location())
    dest.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = dest / f"toolkit_backup_{timestamp}.db"
    shutil.copy2(DB_PATH, backup_file)
    log.info("Backup written to %s", backup_file)

    # Record last backup time
    set_setting("last_backup_at", _now())
    return str(backup_file)


def restore(backup_path: str):
    """
    Replace the live database with a backup file.
    Creates a safety snapshot of the current db first.
    """
    src = Path(backup_path)
    if not src.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")

    # Safety copy of current db
    if DB_PATH.exists():
        safety = DB_PATH.with_suffix(f".pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        shutil.copy2(DB_PATH, safety)
        log.info("Pre-restore safety copy: %s", safety)

    shutil.copy2(src, DB_PATH)
    log.info("Restored database from %s", backup_path)


def export_json(destination_path: str) -> str:
    """
    Export all projects + their latest state to a single JSON file.
    Returns the path of the file created.
    """
    _init_db()
    dest = Path(destination_path)
    dest.mkdir(parents=True, exist_ok=True)

    projects = list_projects()
    export = []
    for p in projects:
        try:
            state = load_project(p["id"])
            export.append({"project": p, "state": state})
        except ValueError:
            pass  # project with no versions — skip

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = dest / f"toolkit_export_{timestamp}.json"
    out_file.write_text(json.dumps(export, indent=2))
    log.info("JSON export written to %s", out_file)
    return str(out_file)


def list_backups(backup_dir: str = None) -> list[dict]:
    """
    List .db backup files in backup_dir, newest first.
    Each dict has: filename, path, size_mb, modified_at.
    """
    d = Path(backup_dir or get_backup_location())
    if not d.exists():
        return []
    files = sorted(d.glob("toolkit_backup_*.db"), key=lambda f: f.stat().st_mtime, reverse=True)
    return [
        {
            "filename": f.name,
            "path": str(f),
            "size_mb": round(f.stat().st_size / 1_048_576, 2),
            "modified_at": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        }
        for f in files
    ]


# ---------------------------------------------------------------------------
# Auto-backup on startup
# ---------------------------------------------------------------------------

def auto_backup_if_stale(max_age_hours: int = 24):
    """
    Run a backup if no backup has been taken in the last max_age_hours.
    Safe to call on every app start — does nothing if backup is fresh.
    """
    if not DB_PATH.exists():
        return  # Nothing to back up yet

    last = get_setting("last_backup_at")
    if last:
        age_hours = (datetime.now(timezone.utc) - datetime.fromisoformat(last)).total_seconds() / 3600
        if age_hours < max_age_hours:
            return

    try:
        path = backup()
        log.info("Auto-backup completed: %s", path)
    except Exception as e:
        log.warning("Auto-backup failed: %s", e)
