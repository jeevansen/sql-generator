from .basegen import QueryGenerator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from pymongo import MongoClient
from django.db import connection, connections
import logging
import re

class MongoQueryGenerator(QueryGenerator):

    def __init__(self, client, database_name):

        self.client = client
        self.db = client["Project"]  # Set the database
        self.prompt = self.get_prompts(connection)  
        self.table_schemas = self.get_collection_schemas()
        

    def get_prompts(self, connection): 
        if not hasattr(connection, 'cursor'):
            raise TypeError(f"Expected database connection, but got {type(connection)}")

        try:
            with connection.cursor() as cursor:  
                cursor.execute("SELECT prompt FROM public.prompts WHERE db_select = %s", ['mongo'])  
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

    def get_collection_schemas(self):
        self.collection_schemas = {}
        try:
            collections = self.db.list_collection_names()
            logging.debug(f"Collections fetched: {collections}")
            
            if not collections:
                logging.error("No collections found! Check your database.")
                return {}
            
            for collection_name in collections:
                sample_doc = self.db[collection_name].find_one()
                if sample_doc:
                    self.collection_schemas[collection_name] = {key: type(value).__name__ for key, value in sample_doc.items()}
                else:
                    logging.warning(f"No documents found for collection: {collection_name}")
            
            logging.debug(f"Final Collection Schemas: {self.collection_schemas}")
        except Exception as e:
            logging.error(f"Error fetching collection schemas: {str(e)}")
            return {}

        return self.collection_schemas

    def clean_user_query(self, user_input):
        return super().clean_user_query(user_input)

    @login_required
    def nosql_generator(request):
        client = MongoClient("mongodb://localhost:27017/")
        generator = MongoQueryGenerator(client, "Project")
        
        user_input = None
        query = None
        results = None
        
        if request.method == "POST":
            user_input = request.POST.get("user_input", "").strip()
            if user_input:
                try:
                    query = generator.generate_query(user_input)
                except Exception as e:
                    query = f"Error: {str(e)}"
        
        return render(request, "blog/sql1.html", {
            "user_input": user_input,
            "query": query,
            "results": results,
            "response": True
        })


        