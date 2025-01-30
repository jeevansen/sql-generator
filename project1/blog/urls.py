from django.urls import path
from . import views
from .views import DatabaseSchemaExtractor
from .views import db_login

urlpatterns = [
    path('', db_login.base, name='blog-home'),  # Landing page or homepage
    path('db_sel/', db_login.database_selection, name='database-selection'),  # Database selection page
    path('sql/', DatabaseSchemaExtractor.sql_generator, name='sql_generator'),# sql generator page
]


