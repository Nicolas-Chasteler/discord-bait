#postgreslogger.py
import logging
import os
from pygres import PostgresHandler



class PostgresLogger(logging.Handler):
    def __init__(self):
        super().__init__()
        self.conn = PostgresHandler().get_cursor().connection
        self.cursor = self.conn.cursor()

    def emit(self, record):
        # Format the log record
        log_entry = self.format(record)
        # Define the insert query
        insert_query = """INSERT INTO logs (level, message, module) VALUES (%s, %s, %s);"""
        # Insert the log into the PostgreSQL database
        self.cursor.execute(insert_query, (record.levelname, log_entry, record.module))
        self.conn.commit()

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

logger = PostgresLogger.initialize_logger()
