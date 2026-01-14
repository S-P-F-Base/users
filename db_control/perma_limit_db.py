from queue import Queue
from typing import Any

from .base_db import BaseDB, SQLTask


class PermaLimitDB(BaseDB):
    _db_name = "perma_limit"

    _worker_started: bool = False
    _queue = Queue()

    @classmethod
    def set_up(cls) -> None:
        sql_t = [
            SQLTask(
                """
                CREATE TABLE IF NOT EXISTS perma_limit (
                    id INTEGER PRIMARY KEY,
                    char_slot INTEGER NOT NULL DEFAULT 0,
                    lore_char_slot INTEGER NOT NULL DEFAULT 0,
                    weight_bytes INTEGER NOT NULL DEFAULT 0
                );
                """
            )
        ]
        super()._init_db(sql_t)

    @classmethod
    def create(
        cls,
        id: int,
        char_slot: int = 0,
        lore_char_slot: int = 0,
        weight_bytes: int = 0,
    ) -> None:
        cls.submit_write(
            SQLTask(
                """
                INSERT INTO perma_limit (id, char_slot, lore_char_slot, weight_bytes)
                VALUES (?, ?, ?, ?)
                """,
                (id, char_slot, lore_char_slot, weight_bytes),
            )
        )

    @classmethod
    def update(
        cls,
        id: int,
        char_slot: int | None = None,
        lore_char_slot: int | None = None,
        weight_bytes: int | None = None,
    ) -> None:
        fields = []
        params: list[Any] = []

        if char_slot is not None:
            fields.append("char_slot = ?")
            params.append(char_slot)

        if lore_char_slot is not None:
            fields.append("lore_char_slot = ?")
            params.append(lore_char_slot)

        if weight_bytes is not None:
            fields.append("weight_bytes = ?")
            params.append(weight_bytes)

        if not fields:
            return

        params.append(id)

        cls.submit_write(
            SQLTask(
                f"""
                UPDATE perma_limit
                SET {", ".join(fields)}
                WHERE id = ?
                """,
                tuple(params),
            )
        )

    @classmethod
    def delete(cls, id: int) -> None:
        cls.submit_write(SQLTask("DELETE FROM perma_limit WHERE id = ?", (id,)))

    @classmethod
    def get(cls, id: int) -> dict[str, Any] | None:
        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT id, char_slot, lore_char_slot, weight_bytes
                FROM perma_limit
                WHERE id = ?
                """,
                (id,),
            )
            row = cur.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "char_slot": row[1],
            "lore_char_slot": row[2],
            "weight_bytes": row[3],
        }
