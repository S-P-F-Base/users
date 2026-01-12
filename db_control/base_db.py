import logging
import sqlite3
from collections.abc import Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from threading import Thread

_DB_DIR = Path("data/dbs")


@dataclass(frozen=True)
class SQLTask:
    sql: str
    params: Sequence | None = None


class BaseDB:
    _db_name: str = ""

    __queue: Queue[SQLTask] = Queue()
    __worker_started = False

    @classmethod
    def __db_path(cls) -> Path:
        return _DB_DIR / f"{cls._db_name}.db"

    @classmethod
    def __connect(cls) -> sqlite3.Connection:
        conn = sqlite3.connect(
            cls.__db_path(),
            timeout=5.0,
            isolation_level=None,
            check_same_thread=False,
        )
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    @classmethod
    def __execute_write(cls, task: SQLTask):
        conn = cls.__connect()
        try:
            conn.execute("BEGIN;")
            conn.execute(task.sql, task.params or ())
            conn.execute("COMMIT;")

        except Exception:
            conn.execute("ROLLBACK;")
            raise

        finally:
            conn.close()

    @classmethod
    def __start_worker(cls):
        if cls.__worker_started:
            return

        cls.__worker_started = True

        def worker():
            while True:
                task = cls.__queue.get()
                try:
                    cls.__execute_write(task)

                except Exception:
                    logging.exception(f"DB {cls._db_name} write failed: {str(task)}")
                    pass

                finally:
                    cls.__queue.task_done()

        Thread(target=worker, daemon=True).start()

    @classmethod
    def _init_db(cls, sql_t: list[SQLTask]) -> None:
        _DB_DIR.mkdir(parents=True, exist_ok=True)
        cls.__start_worker()
        for task in sql_t:
            cls.__queue.put(task)

    @classmethod
    def submit_write(cls, sql_t: SQLTask):
        cls.__queue.put(sql_t)

    @classmethod
    @contextmanager
    def read(cls):
        conn = cls.__connect()
        try:
            yield conn

        finally:
            conn.close()
