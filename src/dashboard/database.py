"""
SQLite database for dashboard real-time metrics.
"""
import sqlite3
import json
import time
from pathlib import Path
from threading import Lock

DB_PATH = Path("logs/dashboard.db")


class DashboardDB:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.lock = Lock()
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    src_ip TEXT,
                    dst_port INTEGER,
                    action TEXT,
                    is_attack BOOLEAN,
                    reward REAL,
                    confidence REAL,
                    reason TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    packets_total INTEGER,
                    attacks_blocked INTEGER,
                    false_positives INTEGER,
                    f1_score REAL,
                    cumulative_reward REAL,
                    active_rules INTEGER
                )
            """)
            conn.commit()

    def log_event(self, src_ip, dst_port, action, is_attack, reward, confidence=0.0, reason=""):
        with self.lock:
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                conn.execute(
                    "INSERT INTO events VALUES (NULL,?,?,?,?,?,?,?,?)",
                    (time.time(), src_ip, dst_port, action, is_attack, reward, confidence, reason)
                )
                conn.commit()

    def log_metrics(self, packets, blocked, fps, f1, reward, rules):
        with self.lock:
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                conn.execute(
                    "INSERT INTO metrics VALUES (NULL,?,?,?,?,?,?,?)",
                    (time.time(), packets, blocked, fps, f1, reward, rules)
                )
                conn.commit()

    def get_recent_events(self, limit=100):
        with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_metrics_history(self, minutes=5):
        with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
            conn.row_factory = sqlite3.Row
            cutoff = time.time() - (minutes * 60)
            cursor = conn.execute(
                "SELECT * FROM metrics WHERE timestamp > ? ORDER BY timestamp",
                (cutoff,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self):
        with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
            conn.row_factory = sqlite3.Row
            
            total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            attacks = conn.execute("SELECT COUNT(*) FROM events WHERE is_attack=1").fetchone()[0]
            legit = total - attacks
            
            blocks = conn.execute("SELECT COUNT(*) FROM events WHERE action='BLOCK'").fetchone()[0]
            allows = conn.execute("SELECT COUNT(*) FROM events WHERE action='ALLOW'").fetchone()[0]
            limits = conn.execute("SELECT COUNT(*) FROM events WHERE action='RATE-LIMIT'").fetchone()[0]
            
            fps = conn.execute(
                "SELECT COUNT(*) FROM events WHERE action='BLOCK' AND is_attack=0"
            ).fetchone()[0]
            
            return {
                "total_events": total,
                "attacks": attacks,
                "legitimate": legit,
                "blocks": blocks,
                "allows": allows,
                "rate_limits": limits,
                "false_positives": fps,
                "fp_rate": round(fps / blocks, 4) if blocks > 0 else 0.0
            }


db = DashboardDB()
