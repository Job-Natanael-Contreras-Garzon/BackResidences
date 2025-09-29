from django.urls import path
from . import views

urlpatterns = [
    # Define your URL patterns for the residences app here
    path('', views.index, name='index'),  # Example path
    # Add more paths as needed
]