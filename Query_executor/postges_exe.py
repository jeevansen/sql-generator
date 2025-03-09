import psycopg2
import json
from psycopg2.extras import DictCursor

class QueryExecutor:
    def __init__(self, db_connection):
        """
        Initializes QueryExecutor with a persistent PostgresDBConnection instance.
        
        :param db_connection: An instance of PostgresDBConnection.
        """
        self.db_connection = db_connection


    def execute_query(self, query , params=None, output_file="output.json"):
        
        """
        Executes the given SQL query and returns the results in JSON format.

        :param query: SQL query string to execute (passed as a variable).
        :param params: Optional parameters for parameterized queries.
        :param output_file: File path to save JSON results (default: output.json).
        :return: JSON object for SELECT queries, else success message.
        :raises ValueError: If the query is empty or None.
        :raises Exception: If query execution fails.
        """
        if not query:
            raise ValueError("Empty query provided")

        try:
            cursor = self.db_connection.connection.cursor(cursor_factory=DictCursor)
            cursor.execute(query, params)

            # Fetch results if it's a SELECT query
            if query.strip().lower().startswith("select"):
                columns = [desc[0] for desc in cursor.description]  # Extract column names
                rows = cursor.fetchall()
                result = [dict(zip(columns, row)) for row in rows]  # Convert to JSON format
                
                with open(output_file, "w", encoding="utf-8") as json_file:
                    json.dump(result, json_file, indent=4)

                return {"status": "success", "data": result, "file": output_file}  # Return JSON response

            # Commit changes for INSERT/UPDATE/DELETE queries
            self.db_connection.connection.commit()
            return {"status": "success", "rows_affected": cursor.rowcount}

        except Exception as e:
            self.db_connection.connection.rollback()
            raise Exception(f"Query execution failed: {str(e)}")

# Example usage
# query = "SELECT * FROM customers WHERE loyalty_tier = %s;"
# params = ("Platinum",)

# Assuming you have a `db_connection` object initialized
# executor = QueryExecutor(db_connection)
# response = executor.execute_query(query, params)
# print(response)  # This will return JSON data and save it to a file
