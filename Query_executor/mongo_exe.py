import json
from pymongo import MongoClient

class MongoQueryExecutor:
    def __init__(self, db_connection):
        """
        Initializes MongoQueryExecutor with a persistent MongoDB connection instance.

        :param db_connection: An instance of MongoDB connection.
        """
        self.db_connection = db_connection

    def execute_query(self, query, output_file="output.json"):
        """
        Executes the given MongoDB query and returns the results in JSON format.

        :param query: Executable MongoDB query containing collection names.
        :param output_file: File path to save JSON results (default: output.json).
        :return: JSON object with query results.
        :raises Exception: If query execution fails.
        """
        try:
            result = eval(f"self.db_connection.{query}")  # Executes the provided MongoDB query
            
            if isinstance(result, list) or isinstance(result, dict):
                with open(output_file, "w", encoding="utf-8") as json_file:
                    json.dump(result, json_file, indent=4)
                return {"status": "success", "data": result, "file": output_file}
            
            return {"status": "success", "data": result}
        
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")

# Example usage
# query = "customers.find({'loyalty_tier': 'Platinum'}, {'_id': 0})"
# executor = MongoQueryExecutor(mongo_db)
# response = executor.execute_query(query)
# print(response)
