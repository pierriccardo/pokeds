import os
import sqlite3
import logging
import seaborn as sns
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class DB:
    def __init__(self, name: str = "logs.db") -> None:
        self.name = name
        self.create_table()

    def connect(self):
        return sqlite3.connect(self.name)

    def size(self) -> float:
        return os.path.getsize(self.name)

    def create_table(self):
        """Initialize database table."""

        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id TEXT PRIMARY KEY,
                format TEXT,
                rating INTEGER,
                log TEXT
            )
        """
        )
        conn.commit()
        conn.close()

    def add(self, log_id, format, rating, log):
        """Add a log to database if not present."""

        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO logs (id, format, rating, log)
                VALUES (?, ?, ?, ?)
            """,
                (log_id, format, rating, log),
            )
            conn.commit()
            logger.info(f"Log {log_id} added successfully.")
        except sqlite3.IntegrityError:
            logger.debug(f"log ID ({log_id}) already exists.")
        conn.close()

    def exists(self, id: str) -> bool:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM logs WHERE id == '{id}'")
        exists = cursor.fetchone()[0] > 0
        conn.close()
        return exists

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------
    def stats(self) -> dict:
        print("ok")
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM logs")
        count = cursor.fetchone()[0]
        logger.info("DB Stats:")
        logger.info(f"Current size {self.size() / 10**9:.2f} GB")
        logger.info(f"Number of logs: {count}")

        cursor.execute("SELECT COUNT(*) FROM logs WHERE rating IS NULL")
        count = cursor.fetchone()[0]
        logger.info(f"Number of unrated: {count}")
        conn.close()

    def count_logs_by_rating(self, rating_min, rating_max) -> int:
        """
        Count how many logs with a ELO rating between `rating_min`
        and `rating_max` are present in the database.
        """

        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM logs WHERE rating BETWEEN ? AND ?",
            (rating_min, rating_max),
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def count_logs_by_format(self):
        """
        Count the number of logs present in db for each
        distinct format.
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT format, COUNT(*) AS sample_count
            FROM logs
            GROUP BY format;
        """
        )
        results = cursor.fetchall()
        conn.close()

        return zip(*results)
