from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import connections
from django.views import View
import openai
from .schema import get_schema # importring get_schema class from the schema.py file

# Set your OpenAI API key
openai.api_key = ""

class DatabaseSchemaExtractor(View):

    # SQL Query Generation View
    def sql_generator(request, model="gpt-4"):
        connection = connections['default']  # Replace 'default' with your database alias if different

        # Specify the tables you are interested in
        specific_tables = ['products', 'customers', 'orders', 'faq', 'categories']  # Replace with actual table names

        response_text = None

        if request.method == 'POST':
            # Get user input
            user_input = request.POST.get('user_input', '').strip()

            if user_input:
                # Fetch the schemas dynamically
                table_schemas = get_schema().get_table_schemas(connection, specific_tables)

                # Construct the OpenAI prompt
                prompt = f"""
                        You are an intelligent SQL query generator that converts natural language input to sql queries.
                        Your task is to generate proper SQL queries as output.
                        Table schema: {table_schemas}
                        Statement: @@@{user_input}@@@

                        TABLE SCHEMAS AND FORMAT
                        ========================
                        Given above are the table schemas and the table names\
                        delimited by ### and a statement delimited by @@@. 

                        You need to consider the above table schemas and table names\
                        which are related to the domain of airline marketplace.
                        Use only the table names specified between ### and refer exclusively\
                        to the column details from the table schemas provided between ###.
                        Each table schema is given as a dictionary, with column names as keys and values\
                        formatted as type, explanation. Use this information to ensure accurate column names\
                        and types in the SQL query.

                        INPUT STATEMENT
                        ===============
                        The statement is a query by a customer given in English language.
                        Your task is to interpret the statement \
                        and convert it into a proper SQL query. 
                        The table names are given and delimited by ###. Use only those names when\
                        creating the SQL query.

                        OUTPUT STATEMENT
                        ================
                        The query generated will be directly copied and used for querying the database.
                        So, the query should be apt and exact.
                        Make sure the output contains only the SQL query with no additional text or\
                        other characters that are not part of a proper sql query.
                        The query must end with a ';'.

                        OUTPUT FORMAT
                        =============
                        Return the SQL query within a JSON object in the following format:
                        {{
                            "query": "<SQL_QUERY>"
                            "out_of_context": ""
                            "admin":""
                        }}
                        where <SQL_QUERY> is the generated SQL statement.

                        ADMIN CHECK
                        ===========
                        The admin variable is to bet set to Yes if the query contains any commands\
                        like UPDATE, DELETE, ALTER, CREATE, DROP etc., that require admin previleges to  get executed.
                        Otherwise set it to No. In either case set the out_of context variable to.

                        OUT OF CONTEXT CHECK
                        ====================
                        If the statement is unrelated to SQL query generation or references\
                        tables not provided in the schema, return an empty JSON object, with the\
                        out_of_context set to Yes and admin set to \"\".\
                        Otherwise give the output with the variable set to No.


                    """

                # Generate SQL using OpenAI
                try:
                    response = openai.ChatCompletion.create(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=1
                    )

                    # Validate response from OpenAI
                    if 'content' in response.choices[0].message:
                        response_text = response.choices[0].message['content']
                    else:
                        response_text = "Error: No content returned from OpenAI."

                except Exception as e:
                    response_text = f"Error: {str(e)}"

        return render(request, 'blog/sql.html', {'response': response_text})

# Base view for unauthenticated users
class db_login():
    def base(request):
        if request.user.is_authenticated:
            return redirect('database-selection')
        return render(request, 'blog/base.html')

    # View for database selection (authenticated users)
    @login_required
    def database_selection(request):
        return render(request, 'blog/home.html')
