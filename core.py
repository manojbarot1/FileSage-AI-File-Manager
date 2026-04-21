"""
FileSage Core — database, file scanning, file operations
"""
import os
import sqlite3
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any

DB_PATH = os.path.expanduser("~/.filesage/filesage.db")

# ── File type helpers ──────────────────────────────────────────────────────────

READABLE_EXT = {
    ".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml",
    ".toml", ".cfg", ".ini", ".env", ".sh", ".bash", ".html",
    ".css", ".xml", ".csv", ".log", ".rs", ".go", ".java", ".cpp",
    ".c", ".h", ".rb", ".php", ".swift", ".kt", ".sql", ".tf",
    ".vue", ".jsx", ".tsx", ".r", ".scala", ".ex", ".exs",
    ".readme", ".gitignore", ".editorconfig",
}

IMAGE_EXT   = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico", ".bmp", ".tiff"}
VIDEO_EXT   = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}
AUDIO_EXT   = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"}
DOC_EXT     = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt"}
ARCHIVE_EXT = {".zip", ".tar", ".gz", ".rar", ".7z", ".bz2"}


def file_category(ext: str) -> str:
    e = ext.lower()
    if e in IMAGE_EXT:   return "image"
    if e in VIDEO_EXT:   return "video"
    if e in AUDIO_EXT:   return "audio"
    if e in DOC_EXT:     return "document"
    if e in ARCHIVE_EXT: return "archive"
    if e in READABLE_EXT: return "code/text"
    return "other"


def file_icon(ext: str) -> str:
    e = ext.lower()
    if e in IMAGE_EXT:   return "🖼"
    if e in VIDEO_EXT:   return "🎬"
    if e in AUDIO_EXT:   return "🎵"
    if e == ".pdf":      return "📕"
    if e in {".doc",".docx"}: return "📝"
    if e in {".xls",".xlsx"}: return "📊"
    if e in {".ppt",".pptx"}: return "📊"
    if e in ARCHIVE_EXT: return "📦"
    if e == ".py":       return "🐍"
    if e in {".js",".ts",".jsx",".tsx"}: return "📜"
    if e in {".json",".yaml",".yml",".toml"}: return "⚙"
    if e in {".md",".txt"}: return "📄"
    if e in {".sh",".bash"}: return "💻"
    if e in {".html",".css"}: return "🌐"
    return "📄"


def fmt_size(b: int) -> str:
    if not b:
        return "0 B"
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def read_preview(path: str, max_chars: int = 500) -> str:
    try:
        ext = Path(path).suffix.lower()
        if ext in READABLE_EXT or ext == "":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(max_chars).strip()
    except Exception:
        pass
    return ""


# ── Database ───────────────────────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            folder_path TEXT    NOT NULL,
            model_used  TEXT,
            created_at  TEXT    DEFAULT (datetime('now')),
            status      TEXT    DEFAULT 'scanning'
        );
        CREATE TABLE IF NOT EXISTS files (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id        INTEGER,
            original_path     TEXT NOT NULL,
            filename          TEXT,
            parent_folder     TEXT,
            extension         TEXT,
            size_bytes        INTEGER,
            content_preview   TEXT,
            ai_suggested_path TEXT,
            ai_reason         TEXT,
            moved             INTEGER DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
        CREATE TABLE IF NOT EXISTS moves (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            file_id    INTEGER,
            from_path  TEXT,
            to_path    TEXT,
            moved_at   TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


def create_session(folder_path: str) -> int:
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO sessions (folder_path, status) VALUES (?, 'scanning')",
        (folder_path,)
    )
    sid = cur.lastrowid
    conn.commit()
    conn.close()
    return sid


def finish_session(session_id: int, status: str = "scanned", model: str = None) -> None:
    conn = get_db()
    if model:
        conn.execute(
            "UPDATE sessions SET status=?, model_used=? WHERE id=?",
            (status, model, session_id)
        )
    else:
        conn.execute("UPDATE sessions SET status=? WHERE id=?", (status, session_id))
    conn.commit()
    conn.close()


def insert_file(session_id: int, path: str) -> int:
    fname   = os.path.basename(path)
    parent  = os.path.basename(os.path.dirname(path))
    ext     = Path(fname).suffix.lower()
    size    = 0
    preview = ""
    try:
        size    = os.path.getsize(path)
        preview = read_preview(path)
    except Exception:
        pass
    conn = get_db()
    cur  = conn.execute(
        "INSERT INTO files (session_id, original_path, filename, parent_folder, extension, size_bytes, content_preview) VALUES (?,?,?,?,?,?,?)",
        (session_id, path, fname, parent, ext, size, preview),
    )
    fid = cur.lastrowid
    conn.commit()
    conn.close()
    return fid


def update_suggestion(file_id: int, suggested_path: str, reason: str) -> None:
    conn = get_db()
    conn.execute(
        "UPDATE files SET ai_suggested_path=?, ai_reason=? WHERE id=?",
        (suggested_path, reason, file_id)
    )
    conn.commit()
    conn.close()


def get_sessions() -> List[Dict]:
    conn = get_db()
    rows = conn.execute("""
        SELECT s.*,
               COUNT(f.id)   AS file_count,
               SUM(f.moved)  AS moved_count,
               COUNT(CASE WHEN f.ai_suggested_path IS NOT NULL AND f.ai_suggested_path != '' THEN 1 END) AS analyzed_count
        FROM sessions s
        LEFT JOIN files f ON f.session_id = s.id
        GROUP BY s.id
        ORDER BY s.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_session(session_id: int) -> Optional[Dict]:
    conn = get_db()
    row  = conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_files(session_id: int) -> List[Dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM files WHERE session_id=? ORDER BY parent_folder, filename",
        (session_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_session(session_id: int) -> None:
    conn = get_db()
    conn.execute("DELETE FROM moves WHERE session_id=?", (session_id,))
    conn.execute("DELETE FROM files WHERE session_id=?", (session_id,))
    conn.execute("DELETE FROM sessions WHERE id=?",      (session_id,))
    conn.commit()
    conn.close()


def clear_all() -> None:
    conn = get_db()
    conn.execute("DELETE FROM moves")
    conn.execute("DELETE FROM files")
    conn.execute("DELETE FROM sessions")
    conn.commit()
    conn.close()


# ── Scanner ────────────────────────────────────────────────────────────────────

def scan_folder(folder: str, session_id: int, progress_cb=None) -> int:
    """Walk folder, insert every file. Call progress_cb(count) periodically."""
    count = 0
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            if fname.startswith("."):
                continue
            fpath = os.path.join(root, fname)
            try:
                insert_file(session_id, fpath)
                count += 1
                if progress_cb and count % 20 == 0:
                    progress_cb(count)
            except Exception:
                continue
    return count


# ── File Mover ────────────────────────────────────────────────────────────────

def move_files(session_id: int, file_ids: List[int], dry_run: bool = False) -> List[Dict]:
    session  = get_session(session_id)
    base_dir = session["folder_path"]
    conn     = get_db()
    ph       = ",".join("?" * len(file_ids))
    rows     = conn.execute(
        f"SELECT * FROM files WHERE session_id=? AND id IN ({ph}) AND moved=0 AND ai_suggested_path IS NOT NULL AND ai_suggested_path != ''",
        [session_id] + file_ids
    ).fetchall()
    conn.close()

    results = []
    for row in rows:
        f           = dict(row)
        target_dir  = os.path.join(base_dir, f["ai_suggested_path"])
        target_path = os.path.join(target_dir, f["filename"])

        if dry_run:
            results.append({"id": f["id"], "status": "preview",
                             "from": f["original_path"], "to": target_path})
            continue

        try:
            os.makedirs(target_dir, exist_ok=True)
            shutil.move(f["original_path"], target_path)
            conn2 = get_db()
            conn2.execute("UPDATE files SET moved=1 WHERE id=?", (f["id"],))
            conn2.execute(
                "INSERT INTO moves (session_id, file_id, from_path, to_path) VALUES (?,?,?,?)",
                (session_id, f["id"], f["original_path"], target_path),
            )
            conn2.commit()
            conn2.close()
            results.append({"id": f["id"], "status": "moved",
                             "from": f["original_path"], "to": target_path})
        except Exception as e:
            results.append({"id": f["id"], "status": "error", "message": str(e),
                             "from": f["original_path"]})

    return results


def get_stats(session_id: int = None) -> Dict:
    conn = get_db()
    if session_id:
        total    = conn.execute("SELECT COUNT(*) FROM files WHERE session_id=?", (session_id,)).fetchone()[0]
        analyzed = conn.execute("SELECT COUNT(*) FROM files WHERE session_id=? AND ai_suggested_path IS NOT NULL AND ai_suggested_path!=''", (session_id,)).fetchone()[0]
        moved    = conn.execute("SELECT COUNT(*) FROM files WHERE session_id=? AND moved=1", (session_id,)).fetchone()[0]
        size     = conn.execute("SELECT SUM(size_bytes) FROM files WHERE session_id=?", (session_id,)).fetchone()[0] or 0
    else:
        total    = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        analyzed = conn.execute("SELECT COUNT(*) FROM files WHERE ai_suggested_path IS NOT NULL AND ai_suggested_path!=''").fetchone()[0]
        moved    = conn.execute("SELECT COUNT(*) FROM files WHERE moved=1").fetchone()[0]
        size     = conn.execute("SELECT SUM(size_bytes) FROM files").fetchone()[0] or 0
    sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    conn.close()
    return {"total": total, "analyzed": analyzed, "moved": moved, "size": size, "sessions": sessions}


def get_folder_groups(session_id: int) -> List[Dict]:
    conn = get_db()
    rows = conn.execute("""
        SELECT parent_folder,
               COUNT(*) as file_count,
               SUM(size_bytes) as total_size,
               SUM(CASE WHEN ai_suggested_path IS NOT NULL AND ai_suggested_path!='' THEN 1 ELSE 0 END) as analyzed,
               SUM(moved) as moved
        FROM files WHERE session_id=?
        GROUP BY parent_folder ORDER BY file_count DESC
    """, (session_id,)).fetchall()
    groups = []
    for r in rows:
        r = dict(r)
        types = conn.execute("""
            SELECT extension, COUNT(*) as cnt FROM files
            WHERE session_id=? AND parent_folder=?
            GROUP BY extension ORDER BY cnt DESC LIMIT 4
        """, (session_id, r["parent_folder"])).fetchall()
        r["types"] = [dict(t) for t in types]
        groups.append(r)
    conn.close()
    return groups


def get_all_moves() -> List[Dict]:
    conn = get_db()
    rows = conn.execute("""
        SELECT m.*, s.folder_path, f.filename, f.extension
        FROM moves m
        JOIN sessions s ON s.id = m.session_id
        JOIN files f ON f.id = m.file_id
        ORDER BY m.moved_at DESC LIMIT 500
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
