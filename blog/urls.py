from django.urls import path
from . import views
from Query_generator import PostgresQueryGenerator
from users.views import DBLogin
from Query_generator import MongoQueryGenerator

urlpatterns = [
    path('', DBLogin.base, name='blog-home'),  # Landing page or homepage
    path('db_sel/', DBLogin.database_selection, name='database-selection'),  # Database selection page
    path('sql/', PostgresQueryGenerator.sql_generator, name='sql_generator'),  # SQL generator page
    path('nosql/', MongoQueryGenerator.nosql_generator, name='nosql_generator'),  # SQL generator page

]


