from django.urls import path
from .views import get_odoo_data

urlpatterns = [
    path('api/products/', get_odoo_data, name='get_odoo_data'),
    # Add more endpoints here as needed
]