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

    @classmethod
    def _get_queue(cls) -> Queue:
        if cls._queue is None:
            cls._queue = Queue()

        return cls._queue

    @classmethod
    def _db_path(cls) -> Path:
        return _DB_DIR / f"{cls._db_name}.db"

    @classmethod
    def _connect(cls) -> sqlite3.Connection:
        conn = sqlite3.connect(
            cls._db_path(),
            timeout=5.0,
            isolation_level=None,
            check_same_thread=False,
        )
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    @classmethod
    def _execute_write(cls, task: SQLTask):
        conn = cls._connect()
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
    def _start_worker(cls):
        if cls._worker_started:
            return

        cls._worker_started = True
        queue = cls._get_queue()

        def worker():
            while True:
                task = queue.get()
                try:
                    cls._execute_write(task)

                except Exception:
                    logging.exception(f"DB {cls._db_name} write failed: {task}")

                finally:
                    queue.task_done()

        Thread(target=worker, daemon=True).start()

    @classmethod
    def _init_db(cls, sql_t: list[SQLTask]) -> None:
        _DB_DIR.mkdir(parents=True, exist_ok=True)
        cls._start_worker()

        queue = cls._get_queue()
        for task in sql_t:
            queue.put(task)

    @classmethod
    def submit_write(cls, sql_t: SQLTask):
        cls._get_queue().put(sql_t)

    @classmethod
    @contextmanager
    def read(cls):
        conn = cls._connect()
        try:
            yield conn

        finally:
            conn.close()
