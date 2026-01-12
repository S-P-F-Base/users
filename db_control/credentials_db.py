from typing import Any

from db_control.base_db import SQLTask

from .base_db import BaseDB


class CredentialsDB(BaseDB):
    _db_name = "credentials"

    @classmethod
    def set_up(cls) -> None:
        sql_t = [
            SQLTask(
                """
                CREATE TABLE IF NOT EXISTS credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_id TEXT NOT NULL UNIQUE,
                    steam64_id TEXT,
                    dirty INTEGER NOT NULL DEFAULT 1
                );
                """
            )
        ]
        super()._init_db(sql_t)

    @classmethod
    def create(cls, discord_id: str, steam64_id: str | None) -> None:
        cls.submit_write(
            SQLTask(
                "INSERT INTO credentials (discord_id, steam64_id) VALUES (?, ?)",
                (discord_id, steam64_id),
            )
        )

    @classmethod
    def delete(cls, id: int) -> None:
        cls.submit_write(SQLTask("DELETE FROM credentials WHERE id = ?", (id,)))

    @classmethod
    def update(
        cls,
        id: int,
        discord_id: str | None,
        steam64_id: str | None,
    ) -> None:
        fields = []
        params: list[Any] = []

        if discord_id is not None:
            fields.append("discord_id = ?")
            params.append(discord_id)

        if steam64_id is not None:
            fields.append("steam64_id = ?")
            params.append(steam64_id)

        if not fields:
            return

        params.append(id)

        cls.submit_write(
            SQLTask(
                f"UPDATE credentials SET {', '.join(fields)} WHERE id = ?",
                tuple(params),
            )
        )

    @classmethod
    def _get_by(
        cls,
        id: int | None,
        discord_id: str | None,
        steam64_id: str | None,
    ) -> dict[str, Any] | None:
        provided = [
            ("id", id),
            ("discord_id", discord_id),
            ("steam64_id", steam64_id),
        ]

        active = [(name, value) for name, value in provided if value is not None]

        if len(active) != 1:
            raise ValueError("Exactly one lookup key must be provided")

        field, value = active[0]

        with cls.read() as conn:
            cur = conn.execute(
                f"""
                SELECT id, discord_id, steam64_id, dirty
                FROM credentials
                WHERE {field} = ?
                """,
                (value,),
            )
            row = cur.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "discord_id": row[1],
            "steam64_id": row[2],
            "dirty": bool(row[3]),
        }

    @classmethod
    def get_by_id(cls, id: int) -> dict[str, Any] | None:
        return cls._get_by(id=id, discord_id=None, steam64_id=None)

    @classmethod
    def get_by_discord(cls, discord_id: str) -> dict[str, Any] | None:
        return cls._get_by(id=None, discord_id=discord_id, steam64_id=None)

    @classmethod
    def get_by_steam(cls, steam64_id: str) -> dict[str, Any] | None:
        return cls._get_by(id=None, discord_id=None, steam64_id=steam64_id)

    @classmethod
    def set_dirty(cls, id: int) -> None:
        cls.submit_write(
            SQLTask("UPDATE credentials SET dirty = 1 WHERE id = ?", (id,))
        )

    @classmethod
    def clear_dirty(cls, id: int) -> None:
        cls.submit_write(
            SQLTask("UPDATE credentials SET dirty = 0 WHERE id = ?", (id,))
        )
