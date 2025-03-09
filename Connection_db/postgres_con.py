import psycopg2
from psycopg2 import OperationalError
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connections



class PostgresDBConnection:
    def __init__(self):
        self.connection = connections['default']
        self.cursor = None

    def connect(self):
        if not self.is_cursor_active():
            try:
                self.cursor = self.connection.cursor()
                print(" Connected to PostgreSQL via Django settings")
            except OperationalError as e:
                print(f"Connection error: {e}")

    def is_cursor_active(self):
        return self.cursor and not self.cursor.closed

    def execute_query(self, query, params=None):
        if not self.is_cursor_active():
            self.connect()

        try:
            self.cursor.execute(query, params)
            return self.cursor
        except Exception as e:
            print(f" Query execution error: {e}")
            raise e

    def close(self):
        if self.is_cursor_active():
            self.cursor.close()
            print("🔒 Cursor closed")
