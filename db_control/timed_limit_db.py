import time
from queue import Queue
from typing import Any, Literal

from .base_db import BaseDB, SQLTask

TimedLimitStatus = Literal[
    "active",
    "expired",
    "disabled",
]


class TimedLimitDB(BaseDB):
    _db_name = "timed_limit"

    _worker_started: bool = False
    _queue = Queue()

    @classmethod
    def set_up(cls) -> None:
        sql_t = [
            SQLTask(
                """
                CREATE TABLE IF NOT EXISTS timed_limit (
                    uid INTEGER PRIMARY KEY AUTOINCREMENT,
                    id INTEGER NOT NULL,
                    char_slot INTEGER NOT NULL DEFAULT 0,
                    weight_bytes INTEGER NOT NULL DEFAULT 0,
                    expired INTEGER NOT NULL,
                    status TEXT NOT NULL
                );
                """
            ),
            SQLTask(
                "CREATE INDEX IF NOT EXISTS idx_timed_limit_id ON timed_limit (id);"
            ),
            SQLTask(
                "CREATE INDEX IF NOT EXISTS idx_timed_limit_expired ON timed_limit (expired);"
            ),
        ]
        super()._init_db(sql_t)

    @classmethod
    def create(
        cls,
        id: int,
        char_slot: int,
        weight_bytes: int,
        expired: int,
        status: TimedLimitStatus = "active",
    ) -> None:
        cls.submit_write(
            SQLTask(
                """
                INSERT INTO timed_limit
                (id, char_slot, weight_bytes, expired, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (id, char_slot, weight_bytes, expired, status),
            )
        )

    @classmethod
    def update(
        cls,
        uid: int,
        char_slot: int | None = None,
        weight_bytes: int | None = None,
        expired: int | None = None,
        status: TimedLimitStatus | None = None,
    ) -> None:
        fields = []
        params: list[Any] = []

        if char_slot is not None:
            fields.append("char_slot = ?")
            params.append(char_slot)

        if weight_bytes is not None:
            fields.append("weight_bytes = ?")
            params.append(weight_bytes)

        if expired is not None:
            fields.append("expired = ?")
            params.append(expired)

        if status is not None:
            fields.append("status = ?")
            params.append(status)

        if not fields:
            return

        params.append(uid)

        cls.submit_write(
            SQLTask(
                f"""
                UPDATE timed_limit
                SET {", ".join(fields)}
                WHERE uid = ?
                """,
                tuple(params),
            )
        )

    @classmethod
    def delete(cls, uid: int) -> None:
        cls.submit_write(SQLTask("DELETE FROM timed_limit WHERE uid = ?", (uid,)))

    @classmethod
    def get(cls, uid: int) -> dict[str, Any] | None:
        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT uid, id, char_slot, weight_bytes, expired, status
                FROM timed_limit
                WHERE uid = ?
                """,
                (uid,),
            )
            row = cur.fetchone()

        if row is None:
            return None

        return {
            "uid": row[0],
            "id": row[1],
            "char_slot": row[2],
            "weight_bytes": row[3],
            "expired": row[4],
            "status": row[5],
        }

    @classmethod
    def list_by_owner(cls, id: int) -> list[dict[str, Any]]:
        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT uid, id, char_slot, weight_bytes, expired, status
                FROM timed_limit
                WHERE id = ?
                ORDER BY expired
                """,
                (id,),
            )
            rows = cur.fetchall()

        return [
            {
                "uid": row[0],
                "id": row[1],
                "char_slot": row[2],
                "weight_bytes": row[3],
                "expired": row[4],
                "status": row[5],
            }
            for row in rows
        ]

    @classmethod
    def list_active(
        cls,
        id: int,
        now: int | None = None,
    ) -> list[dict[str, Any]]:
        now = now or int(time.time())

        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT uid, id, char_slot, weight_bytes, expired, status
                FROM timed_limit
                WHERE id = ?
                  AND status = 'active'
                  AND expired > ?
                ORDER BY expired
                """,
                (id, now),
            )
            rows = cur.fetchall()

        return [
            {
                "uid": row[0],
                "id": row[1],
                "char_slot": row[2],
                "weight_bytes": row[3],
                "expired": row[4],
                "status": row[5],
            }
            for row in rows
        ]
