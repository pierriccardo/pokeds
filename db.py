import os
import sqlite3
import consts
import logging
import tabulate
import pandas as pd


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
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM logs")
        count = cursor.fetchone()[0]
        logger.info("*" + "-" * 55 + "*")
        logger.info("| Database Stats" + " " * 40 + "|")
        logger.info("*" + "-" * 55 + "*")
        logger.info(f"| Database size     : {self.size() / 10**9:8.2f} GB" + " " * 23 + "|")
        logger.info(f"| Number of logs    : {count:8d}" + " " * 26 + "|")
        cursor.execute("SELECT COUNT(*) FROM logs WHERE rating IS NULL")
        count = cursor.fetchone()[0]
        logger.info(f"| Number of unrated : {count:8d}" + " " * 26 + "|")

        logger.info("*" + "-" * 55 + "*")
        logger.info(f"| {'Count':>10} | {'Format':<41}|")
        logger.info("*" + "-" * 55 + "*")
        data = []
        for format in consts.FORMATS:
            cursor.execute(f"SELECT COUNT(*) FROM logs WHERE format IS '{format}'")
            count = cursor.fetchone()[0]
            logger.info(f"| {count:>10d} | {format:<41}|")
            data.append([count, format])
        conn.close()
        logger.info("*" + "-" * 55 + "*")
        #logger.info("\n" + tabulate.tabulate(data, headers=["Count", "Format"], tablefmt="rst"))


    def count_logs_by_rating(self, rating_ranges: list, formats: list = []) -> pd.DataFrame:
        """
        Query the database to count logs within the specified rating ranges.

        Parameters:
        - rating_ranges: A list of tuples [(min1, max1), (min2, max2), ...]
        - formats: A list of specific formats to filter (optional).

        Returns:
        - A Pandas DataFrame with columns ["Range", "Format", "Count"]
        for direct plotting in Seaborn.
        """
        conn = self.connect()
        cursor = conn.cursor()

        rows = []  # List of dictionaries for DataFrame

        for rating_min, rating_max in rating_ranges:
            rating_range = f"{rating_min}-{rating_max}"

            if formats:  # Query with specific formats
                query = """
                    SELECT format, COUNT(*)
                    FROM logs
                    WHERE rating BETWEEN ? AND ? AND format IN ({})
                    GROUP BY format;
                """.format(",".join("?" * len(formats)))

                cursor.execute(query, [rating_min, rating_max] + formats)

                for format_name, count in cursor.fetchall():
                    rows.append({"Range": rating_range, "Format": format_name, "Count": count})

            else:  # Query without specific formats
                cursor.execute(
                    "SELECT COUNT(*) FROM logs WHERE rating BETWEEN ? AND ?",
                    (rating_min, rating_max)
                )
                count = cursor.fetchone()[0]
                rows.append({"Range": rating_range, "Format": "All", "Count": count})

        conn.close()

        # Convert list of dictionaries to DataFrame
        return pd.DataFrame(rows)

    def count_logs_by_format(self, formats: list = []) -> pd.DataFrame:
        """
        Count the number of logs present in the database for each distinct format.

        Parameters:
        - formats: A list of specific formats to filter (optional).

        Returns:
        - A Pandas DataFrame with columns ["Format", "Count"].
        """
        conn = self.connect()
        cursor = conn.cursor()

        if formats:  # If specific formats are provided
            query = """
                SELECT format, COUNT(*) AS sample_count
                FROM logs
                WHERE format IN ({})
                GROUP BY format;
            """.format(",".join("?" * len(formats)))
            cursor.execute(query, formats)
        else:  # Count for all formats
            query = """
                SELECT format, COUNT(*) AS sample_count
                FROM logs
                GROUP BY format;
            """
            cursor.execute(query)

        # Fetch results and convert to DataFrame
        results = cursor.fetchall()
        conn.close()

        return pd.DataFrame(results, columns=["Format", "Count"])
