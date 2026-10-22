from django.urls import path
from . import views

APP_NAME = 'properties'

urlpatterns = [
    path('', views.property, name='property'),
]