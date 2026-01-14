import logging
from enum import Enum
from pathlib import Path
from typing import Literal

import httpx

log = logging.getLogger(__name__)

OVERLORD_SOCKET = Path("/run/spf/overlord.sock")
USER_GET_TYPE = ["id", "discord", "steam64"]
USER_GET_TYPE_L = Literal["id", "discord", "steam64"]


class Constants:
    _data: dict[str, str] = {}

    @classmethod
    async def req_from_over(cls) -> None:
        transport = httpx.AsyncHTTPTransport(uds=str(OVERLORD_SOCKET))

        try:
            async with httpx.AsyncClient(
                transport=transport,
                timeout=5.0,
            ) as client:
                resp = await client.get("http://overlord/config")

            if resp.status_code != 200:
                log.warning(
                    "Overlord returned %s for %s",
                    resp.status_code,
                    "http://overlord/config",
                )
                cls._data = {}

            cls._data = resp.json()

        except httpx.ConnectError:
            log.warning("Overlord socket not available: %s", OVERLORD_SOCKET)
            cls._data = {}

        except httpx.TimeoutException:
            log.warning("Overlord request timeout: %s", "http://overlord/config")
            cls._data = {}

        except Exception as exc:
            log.exception(
                "Unexpected error while fetching %s: %s",
                "http://overlord/config",
                exc,
            )
            cls._data = {}

    @classmethod
    def get_all_const(cls) -> dict[str, str]:
        return cls._data


class AccessKeys(Enum):
    """
    Енум с базовыми правами и доступами
    value[0] - ключ
    value[1] - значение по умолчанию
    """

    ALL = "all_access", False
    """Позволяет байпасать абсолютно все права"""

    CREATE_USER = "create_user", False
    """Позволяет создавать пользователя"""
    UPDATE_USER = "update_user", False
    """Позволяет обновлять пользователя"""
    DELETE_USER = "delete_user", False
    """Позволяет удалять пользователя"""

    UPDATE_TIMED_LIMIT = "update_timed_limit", False
    """Позволяет менять временный лимит"""
    UPDATE_PERMA_LIMIT = "update_perma_limit", False
    """Позволяет менять перманентный лимит"""

    CREATE_DB_CHAR = "create_db_char", False
    """Позволяет создавать персонажей игрока"""
    UPDATE_DB_CHAR = "update_db_char", False
    """Позволяет обновлять персонажей игрока"""
    DELETE_DB_CHAR = "delete_db_char", False
    """Позволяет удалять персонажей игрока"""

    UPDATE_ACCESS = "update_access", False
    """Позволяет менять доступ"""

    UPDATE_NOTE = "update_note", False
    """Позволяет апдейтить записи людей"""

    UPDATE_BLACK_LIST = "update_black_list", False
    """Позволяет обновлять чёрный список"""

    @classmethod
    def get_all_access_keys(cls) -> list[str]:
        return [x.value[0] for x in list(cls)]

    @classmethod
    def get_base_access(cls) -> dict[str, bool]:
        return {x.value[0]: x.value[1] for x in list(cls)}
