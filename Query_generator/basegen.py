from django.db import connection
import re
import openai
from django.conf import settings
import os
import json
import logging

logging.basicConfig(level=logging.DEBUG)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project1.settings")

class QueryGenerator():
    def __init__(self, connection):
        if not hasattr(connection, "cursor"): 
            raise TypeError(f"Expected database connection, but got {type(connection)}")
        self.prompt = self.get_prompts(connection)  
        self.table_schemas = self.get_table_schemas(connection)

    def get_prompts(self):
        pass

    def get_table_schemas(self):
        pass

    def clean_user_query(self, user_input):  
        if not isinstance(user_input, str) or not user_input.strip():
            return None  
        user_input = re.sub(r"[^\w\s,.]", "", user_input)
        cleaned_input = " ".join(user_input.split())
        return cleaned_input
    
    def clean_response(self, response):
        if not response:
            return {}
        cleaned = re.sub(r'```(json)?\n?|\n```', '', str(response))
        try:
            return json.loads(cleaned)
        except Exception as e:
            print('ERROR from clean responce is' ,e)
            return {}
    

    def generate_query(self, user_query, model="gpt-4o-mini"):
        cleaned_input = self.clean_user_query(user_query)
        if not cleaned_input:
            raise ValueError("Invalid user query")
        
        openai.api_key = settings.OPENAI_API_KEY
        try:
            
            logging.debug(f"Original Prompt from DB: {self.prompt}")
            logging.debug(f"Fetched Table Schemas Before Replacement: {self.table_schemas}")

            formatted_prompt = self.prompt.replace("{table_schemas}", str(self.table_schemas))
            formatted_prompt = formatted_prompt.replace("@@@{user_input}@@@", cleaned_input)

            logging.debug(f"Final Prompt after Placeholder Replacement: {formatted_prompt}")

            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": formatted_prompt},
                    {"role": "user", "content": cleaned_input}
                ]
            )
            generated_query = response.choices[0].message.content
            return self.clean_response(generated_query)
        except Exception as e:
            raise Exception(f"Error generating query: {str(e)}")