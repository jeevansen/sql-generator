from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import openai

# Set your OpenAI API key
openai.api_key = "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"

global user_input
user_input = " "

class BaseView(View):
    def get(self, request):
        if request.user.is_authenticated:
            # Redirect to the database selection page if logged in
            return redirect('database-selection')
        # Render the home page for non-authenticated users
        return render(request, 'blog/base.html')

@method_decorator(login_required, name='dispatch')
class DatabaseSelectionView(View):
    def get(self, request):
        # Render the database selection page for authenticated users
        return render(request, 'blog/home.html')

class SQLGeneratorView(View):
    template_name = 'blog/sql.html'
    model = "gpt-4o-mini"

    tables = ['categories', 'products', 'customers', 'orders', 'faq']

    global user_input  # Declare the use of the global variable 'user_input'
    response_text = None
    categories = {'id': 'integer, primary key ', 
                  'category_name': 'varchar'
    }

    products = {'asin': 'varchar, primary key', 
                'title': 'text',
                'imgurl': 'text',
                'stars': 'float',
                'price': 'float',
                'category_id': "integer, Foreign Key from categories table",
                'isbestseller': 'boolean, false or true',
                'boughtinlastmonth': 'integer'
            }

    customers = {'customer_id': 'integer, primary key', 
                 'first_name': 'varchar',
                 'last_name': 'varchar',
                 'email': 'text',
                 'phone_number': 'varchar',
                 'date_of_birth': "date ",
                 'nationality': 'text',
                 'address': 'text',
                 'freq_flyer_number': 'varchar, unique frequent flyer number of the customer',
                 'loyalty_id': 'varchar',
                 'lotyalty_tier': 'varchar,(gold, silver, platinum)',
                 'loyalty_points': 'integer',
                 'status': 'varchar'
                }
    orders = {
                'history_id': 'integer, primary key of the table',
                'product_id': 'varchar, foreign key referencing the primary key \'asin\' of the products table',
                'customer_id': 'integer, foreign key referencing the primary key \'customer_id\' of the customers table',
                'FFN': 'varchar',
                'quantity': 'integer',
                'price_per_unit': 'numeric',
                'total_price': 'numeric',
                'order_date': 'date',
                'status': 'varchar,(e.g., pending, shipped, delivered)',
                'shipment_date': 'date',
                'mode_of_delivery': 'varchar,(e.g., air, ground)',
                'delivery_location': 'varchar',
                'payment_method': 'varchar,(e.g., credit card, PayPal)',
                'payment_status': 'varchar,  (e.g., paid, pending)',
                'payment_transaction_ref_id': 'varchar',
                'payment_date': 'date',
                'currency': 'varchar',
                'tax_amount': 'numeric',
                'discount_amount': 'numeric',
                'baggage_service': 'boolean',
                'boarding_pass_required': 'boolean',
                'flight_details': 'varchar',
                'loyalty_points_earned': 'integer',
                'loyalty_points_redeemed': 'integer',
                'return_status': 'varchar',
                'refund_amount': 'numeric',
                'refund_date': 'date',
                'duty_free_eligibility': 'boolean',
                'duty_free_limit': 'integer',
                'customs_clearance_required': 'boolean',
                'special_instructions': 'varchar',
                'created_at': 'timestamp',
                'updated_at': 'timestamp'
            }

    faq = {
                'faq_id': 'integer, primary key of the table',
                'customer_id': "integer, foreign key referencing the primary key 'customer_id' of the customers table",
                'product_id': "varchar, foreign key referencing the primary key 'asin' of the products table",
                'product_name': 'text',
                'faq_category': 'varchar,(e.g., product-related, payment-related)',
                'faq_question': 'text',
                'faq_answer': 'text',
                'faq_datetime': 'timestamp'
            }
    tables=['categories', 'products', 'customers', 'orders', 'faq']
    
    prompt = f"""
    You are an intelligent SQL query generator that converts natural language input to sql queries.
    Your task is to generate proper SQL queries as output.
    Table schema: ###{products}, {categories}, {customers}, {orders}, {faq}###
    Table names: ###{tables}###
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

    def get_prompt(self, user_input):
        return self.prompt_template.format(
            schemas=self.schemas, tables=self.tables, user_input=user_input
        )

    def post(self, request):
        global user_input
        user_input = request.POST.get('user_input', '').strip()
        response_text = None

        if user_input:
            prompt = self.get_prompt(user_input)
            try:
                messages = [{"role": "user", "content": prompt}]
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=1
                )

                response_text = response.choices[0].message['content']
            except Exception as e:
                response_text = f"Error: {str(e)}"

        return render(request, self.template_name, {'response': response_text})