import json
from queue import Queue
from typing import Any

from .base_db import BaseDB, SQLTask


class DbCharDB(BaseDB):
    _db_name = "db_char"

    _worker_started: bool = False
    _queue = Queue()

    @classmethod
    def set_up(cls) -> None:
        sql_t = [
            SQLTask(
                """
                CREATE TABLE IF NOT EXISTS db_char (
                    uid INTEGER PRIMARY KEY AUTOINCREMENT,
                    id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    discord_url TEXT,
                    char_type TEXT NOT NULL,
                    content_ids BLOB NOT NULL,
                    game_db_id INTEGER
                );
                """
            ),
            SQLTask("CREATE INDEX IF NOT EXISTS idx_db_char_id ON db_char (id);"),
        ]
        super()._init_db(sql_t)

    @classmethod
    def create(
        cls,
        id: int,
        name: str,
        char_type: str,
        content_ids: list[str],
        discord_url: str | None = None,
        game_db_id: int | None = None,
    ) -> None:
        payload = json.dumps(content_ids, ensure_ascii=False)

        cls.submit_write(
            SQLTask(
                """
                INSERT INTO db_char
                (id, name, discord_url, char_type, content_ids, game_db_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (id, name, discord_url, char_type, payload, game_db_id),
            )
        )

    @classmethod
    def update(
        cls,
        uid: int,
        name: str | None = None,
        discord_url: str | None = None,
        char_type: str | None = None,
        content_ids: list[str] | None = None,
        game_db_id: int | None = None,
    ) -> None:
        fields = []
        params: list[Any] = []

        if name is not None:
            fields.append("name = ?")
            params.append(name)

        if discord_url is not None:
            fields.append("discord_url = ?")
            params.append(discord_url)

        if char_type is not None:
            fields.append("char_type = ?")
            params.append(char_type)

        if content_ids is not None:
            fields.append("content_ids = ?")
            params.append(json.dumps(content_ids, ensure_ascii=False))

        if game_db_id is not None:
            fields.append("game_db_id = ?")
            params.append(game_db_id)

        if not fields:
            return

        params.append(uid)

        cls.submit_write(
            SQLTask(
                f"""
                UPDATE db_char
                SET {", ".join(fields)}
                WHERE uid = ?
                """,
                tuple(params),
            )
        )

    @classmethod
    def delete(cls, uid: int) -> None:
        cls.submit_write(SQLTask("DELETE FROM db_char WHERE uid = ?", (uid,)))

    @classmethod
    def get(cls, uid: int) -> dict[str, Any] | None:
        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT uid, id, name, discord_url, char_type, content_ids, game_db_id
                FROM db_char
                WHERE uid = ?
                """,
                (uid,),
            )
            row = cur.fetchone()

        if row is None:
            return None

        try:
            content_ids = json.loads(row[5])

        except Exception:
            content_ids = []

        return {
            "uid": row[0],
            "id": row[1],
            "name": row[2],
            "discord_url": row[3],
            "char_type": row[4],
            "content_ids": content_ids,
            "game_db_id": row[6],
        }

    @classmethod
    def list_by_owner(cls, id: int) -> list[dict[str, Any]]:
        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT uid, id, name, discord_url, char_type, content_ids, game_db_id
                FROM db_char
                WHERE id = ?
                ORDER BY uid
                """,
                (id,),
            )
            rows = cur.fetchall()

        out: list[dict[str, Any]] = []

        for row in rows:
            try:
                content_ids = json.loads(row[5])

            except Exception:
                content_ids = []

            out.append(
                {
                    "uid": row[0],
                    "id": row[1],
                    "name": row[2],
                    "discord_url": row[3],
                    "char_type": row[4],
                    "content_ids": content_ids,
                    "game_db_id": row[6],
                }
            )

        return out
