#postgreslogger.py
import logging
import os
import psycopg2
from psycopg2 import sql



class PostgresLogger(logging.Handler):
    def __init__(self):
        super().__init__()

        print(os.environ)

        # Get connection info
        dbname = os.getenv("PG_NAME", "logger")
        user = os.getenv("PG_USER", "logger")
        password = os.getenv("PG_PASSWORD", "postgres")
        host = os.getenv("PG_HOST", "localhost")
        port = os.getenv("PG_PORT", 5432)

        self.conn = psycopg2.connect(database=dbname, user=user, host=host, password=password, port=port)
        self.cursor = self.conn.cursor()

        self._create_table_if_not_exist()

    def _create_table_if_not_exist(self):
        create_table = """
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            level VARCHAR(50),
            message TEXT,
            module VARCHAR(100)
        );
        """

        try:
            self.cursor.execute(create_table)
            self.conn.commit()
        except Exception as e:
            print(f"Failed to create table: {e}")
            self.conn.rollback()

    def emit(self, record):
        # Format the log record
        log_entry = self.format(record)
        # Define the insert query
        insert_query = sql.SQL(
            "INSERT INTO logs (level, message, module) VALUES (%s, %s, %s)"
        )
        # Insert the log into the PostgreSQL database
        try:
            self.cursor.execute(insert_query, (record.levelname, log_entry, record.module))
            self.conn.commit()
        except Exception as e:
            print(f"Failed to insert log entry: {e}")
            self.conn.rollback()

    def close(self):
        self.cursor.close()
        self.conn.close()
        super().close()

    @staticmethod
    def initialize_logger():
        logger = logging.getLogger('discord-bait')
        logger.setLevel(logging.DEBUG)
        pg_handler = PostgresLogger()
        logger.addHandler(pg_handler)
        return logger

