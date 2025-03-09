from .basegen import QueryGenerator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection, connections
import logging
import re
import json

class PostgresQueryGenerator(QueryGenerator):


        
    def __init__(self, connection):
        super().__init__(connection)
        

    def get_prompts(self, connection): 
        if not hasattr(connection, 'cursor'):
            raise TypeError(f"Expected database connection, but got {type(connection)}")

        try:
            with connection.cursor() as cursor:  
                cursor.execute("SELECT prompt FROM public.prompts WHERE db_select = %s", ['postgres'])  
                row = cursor.fetchone()
                
                if row:
                    raw_prompt = row[0]
                    cleaned_prompt = raw_prompt.encode('utf-8').decode('utf-8')
                    cleaned_prompt = cleaned_prompt.replace("\\n", "\n").replace("\\\"", "\"")
                    cleaned_prompt = re.sub(r'\\+', '', cleaned_prompt)
                    return cleaned_prompt
                else:
                    return "Default prompt"

        except Exception as e:
            print(f"Error fetching prompt: {str(e)}")  
            return "Error: Could not fetch prompt"

    def get_table_schemas(self, connection):
        self.table_schemas = {}

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]

            logging.debug(f"Tables fetched: {tables}")

            if not tables:
                logging.error("No tables found! Check your database and schema.")
                return {}

            for table_name in tables:
                cursor.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = %s
                """, [table_name])

                columns = cursor.fetchall()
                logging.debug(f"Columns for {table_name}: {columns}")

                if not columns:
                    logging.warning(f"No columns found for table: {table_name}")
                    continue

                self.table_schemas[table_name] = {col[0]: col[1] for col in columns}

            logging.debug(f"Final Table Schemas: {self.table_schemas}")

        return self.table_schemas


    def clean_user_query(self, user_input):
        return super().clean_user_query(user_input)
    
    @login_required
    def sql_generator(request):
        connection = connections['default']
        generator = PostgresQueryGenerator(connection)
        
        user_input = None
        query = None
        results = None
        
        if request.method == 'POST':
            user_input = request.POST.get('user_input', '').strip()
            if user_input:
                try:
                    query = generator.generate_query(user_input)
                except Exception as e:
                    query = f"Error: {str(e)}"
        return render(request, 'blog/sql.html', {
            'user_input': user_input,
            'query': query,
            'results': results,
            'response': True
        })
    

