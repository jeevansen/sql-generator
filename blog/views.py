from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import connections
from django.views import View
import logging
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Query_generator import PostgresQueryGenerator
from Query_executor import postges_exe

logger = logging.getLogger(__name__)

class ChatResponseHandler(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Handle POST requests for generating SQL queries."""
        try:
            logger.debug(f"Parsed request data: {request.data}")
            chat_id = request.data.get('id')
            user_input = request.data.get('user_input')
            db_selected = request.data.get('no_sql', 'sql')  
            logger.debug(f"Received chat_id: {chat_id}, query_string: {user_input}, db_selected: {db_selected}")

            if not user_input:
                logger.error("Missing 'user_input' parameter.")
                return Response(
                    {"error": "Missing 'user_input' parameter."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if db_selected == "sql":
                logger.debug("Generating SQL query.")
                connection = connections['default']
                generator = PostgresQueryGenerator(connection)
                sql_query = generator.generate_query(user_input)
                
                logger.debug(f"Generated SQL query: {sql_query}")
                
                return Response(data={"result": sql_query}, status=status.HTTP_200_OK)
            else:
                logger.debug("Generating non-SQL query.")
                non_sql_query = "Generated non-SQL query based on the request."
                return Response(data={"result": non_sql_query}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An error occurred while processing request: {str(e)}", exc_info=True)
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
