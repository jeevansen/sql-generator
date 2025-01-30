from django.views import View

class get_schema(View):
    def get_table_schemas(self, connection, specific_tables):
        table_schemas = {}
        with connection.cursor() as cursor:
            for table_name in specific_tables:
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = %s
                """, [table_name])
                if cursor.fetchone():  # If the table exists
                    # Fetch schema details for the table
                    cursor.execute("""
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_name = %s
                    """, [table_name])
                    table_schemas[table_name] = cursor.fetchall()
                else:
                    table_schemas[table_name] = f"Table '{table_name}' does not exist."

        return table_schemas