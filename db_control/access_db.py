import json
from queue import Queue
from typing import Any

from .base_db import BaseDB, SQLTask


class AccessDB(BaseDB):
    _db_name = "access"

    _worker_started: bool = False
    _queue = Queue()

    @classmethod
    def set_up(cls) -> None:
        sql_t = [
            SQLTask(
                """
                CREATE TABLE IF NOT EXISTS access (
                    id INTEGER PRIMARY KEY,
                    version INTEGER NOT NULL DEFAULT 0,
                    access BLOB NOT NULL
                );
                """
            )
        ]
        super()._init_db(sql_t)

    @classmethod
    def create(
        cls,
        id: int,
        version: int = 0,
        access: dict[str, bool] | None = None,
    ) -> None:
        payload = json.dumps(access or {}, ensure_ascii=False)

        cls.submit_write(
            SQLTask(
                """
                INSERT INTO access (id, version, access)
                VALUES (?, ?, ?)
                """,
                (id, version, payload),
            )
        )

    @classmethod
    def update(
        cls,
        id: int,
        version: int | None = None,
        access: dict[str, bool] | None = None,
    ) -> None:
        fields = []
        params: list[Any] = []

        if version is not None:
            fields.append("version = ?")
            params.append(version)

        if access is not None:
            fields.append("access = ?")
            params.append(json.dumps(access, ensure_ascii=False))

        if not fields:
            return

        params.append(id)

        cls.submit_write(
            SQLTask(
                f"""
                UPDATE access
                SET {", ".join(fields)}
                WHERE id = ?
                """,
                tuple(params),
            )
        )

    @classmethod
    def delete(cls, id: int) -> None:
        cls.submit_write(SQLTask("DELETE FROM access WHERE id = ?", (id,)))

    @classmethod
    def get(cls, id: int) -> dict[str, Any] | None:
        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT id, version, access
                FROM access
                WHERE id = ?
                """,
                (id,),
            )
            row = cur.fetchone()

        if row is None:
            return None

        try:
            access_data = json.loads(row[2])

        except Exception:
            access_data = {}

        return {
            "id": row[0],
            "version": row[1],
            "access": access_data,
        }

    @classmethod
    def get_by_version(
        cls,
        version: int = 0,
    ) -> list[dict[str, Any]]:
        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT id, version, access
                FROM access
                WHERE version = ?
                """,
                (version,),
            )
            rows = cur.fetchall()

        out: list[dict[str, Any]] = []

        for id_, ver, raw_access in rows:
            try:
                access_data = json.loads(raw_access)

            except Exception:
                access_data = {}

            out.append(
                {
                    "id": id_,
                    "version": ver,
                    "access": access_data,
                }
            )

        return out
