import sqlite3
from datetime import datetime
from typing import Optional, List, Dict


class Database:
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.init_db()

    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    plan TEXT DEFAULT NULL,
                    expiry TIMESTAMP DEFAULT NULL,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_payment_check TIMESTAMP DEFAULT NULL
                )
            """)
            conn.commit()

    def add_user(self, user_id: int, username: str):
        with self.get_conn() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO users (user_id, username)
                VALUES (?, ?)
            """, (user_id, username))
            conn.commit()

    def get_user(self, user_id: int) -> Optional[Dict]:
        with self.get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
            if not row:
                return None
            user = dict(row)
            if user.get("expiry"):
                user["expiry"] = datetime.fromisoformat(user["expiry"])
            return user

    def activate_user(self, user_id: int, plan: str, expiry: datetime):
        with self.get_conn() as conn:
            conn.execute("""
                UPDATE users SET plan = ?, expiry = ?
                WHERE user_id = ?
            """, (plan, expiry.isoformat(), user_id))
            conn.commit()

    def get_active_users(self) -> List[Dict]:
        with self.get_conn() as conn:
            rows = conn.execute("""
                SELECT * FROM users
                WHERE plan IS NOT NULL
                AND expiry > ?
            """, (datetime.now().isoformat(),)).fetchall()
            users = []
            for row in rows:
                user = dict(row)
                if user.get("expiry"):
                    user["expiry"] = datetime.fromisoformat(user["expiry"])
                users.append(user)
            return users

    def update_payment_check(self, user_id: int):
        with self.get_conn() as conn:
            conn.execute("""
                UPDATE users SET last_payment_check = ?
                WHERE user_id = ?
            """, (datetime.now().isoformat(), user_id))
            conn.commit()

    def get_stats(self) -> Dict:
        with self.get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            active = conn.execute(
                "SELECT COUNT(*) FROM users WHERE plan IS NOT NULL AND expiry > ?",
                (datetime.now().isoformat(),)
            ).fetchone()[0]
            basic = conn.execute(
                "SELECT COUNT(*) FROM users WHERE plan = 'basic' AND expiry > ?",
                (datetime.now().isoformat(),)
            ).fetchone()[0]
            pro = conn.execute(
                "SELECT COUNT(*) FROM users WHERE plan = 'pro' AND expiry > ?",
                (datetime.now().isoformat(),)
            ).fetchone()[0]
            premium = conn.execute(
                "SELECT COUNT(*) FROM users WHERE plan = 'premium' AND expiry > ?",
                (datetime.now().isoformat(),)
            ).fetchone()[0]

            revenue = (basic * 5) + (pro * 10) + (premium * 20)
            return {
                "total": total,
                "active": active,
                "basic": basic,
                "pro": pro,
                "premium": premium,
                "revenue": revenue
            }
