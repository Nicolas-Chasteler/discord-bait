#postgreslogger.py
import logging
import os
import psycopg2
from psycopg2 import sql



class PostgresLogger(logging.Handler):
    def __init__(self):
        super().__init__()

        # Get connection info
        dbname = os.getenv("PG_NAME", "logger")
        user = os.getenv("PG_USER", "logger")
        password = os.getenv("PG_PASSWORD", "password")
        host = os.getenv("PG_HOST", "localhost")
        port = os.getenv("PG_PORT", 5432)

        # Connect to PG
        self.dsn = f"dbname={dbname} user={user} password={password} host={host} port={port}"
        self.conn = psycopg2.connect(self.dsn)
        self.cursor = self.conn.cursor()

        # Create tables
        self.create_tables()

    # Execute arbitrary sql file and save record to pg_scripts
    def execute_sql_file(self, sql_file_path):
        # Open sql file
        with open(sql_file_path, 'r') as file:
            sql = file.read()

            # Run sql file
            try:
                self.cursor.execute(sql)
                self.conn.commit()
            except Exception as e:
                print(f"Failed to run script: {file}")
                print(f"{e}")
                self.conn.rollback()

            # Inserting record of save into pg_scripts
            insert_record = sql.SQL(
                "INSERT INTO pg_scripts (id, file_name) VALUES (%s, %s)"
            )

            # Save record of execution to pg_scripts
            try:
                self.cursor.execute(sql, (int(file.split("__")[0]), file))
                self.conn.commit()
            except Exception as e:
                print(f"Failed to save to pg_scripts: {file}")
                print(f"{e}")
                self.conn.rollback()

    def check_execution(self, file_name):
        # Returns true if pg_scripts exists
        check_query = """
        SELECT EXISTS (
            SELECT 1
            FROM pg_scripts
            WHERE file_name = %s
        );
        """

        # Execute query
        self.cursor.execute(check_query, (file_name))
        exists = cursor.fetchone()[0]
        return exists

    def create_tables(self):
        # Create pg_scripts if not exists
        self._check_pg_scripts()

        # Get all pg_scripts
        folder_path = "./sql_scripts"
        sql_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".sql")])

        for file_name in sql_files:
            file_path = os.path.join(folder_path, file_name)

            # Check if script has already been run
            if self.check_execution(file_name):
                # Run script
                self.execute_sql_file(file_path)

    # Check if pg_scripts table exists, if not create
    def _check_pg_scripts(self):
        # Checks if pg_scripts exists
        check_query = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'pg_scripts'
        );
        """
        self.cursor.execute(query)
        exists = cursor.fetchone()[0]

        if not exists:
            self.execute_sql_file()

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

logger = PostgresLogger.initialize_logger()
