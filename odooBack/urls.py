from django.urls import path
from .views import get_products, get_moves, get_delivery_orders, get_receipts, get_product_by_id, update_product, delete_product, add_product, get_product_categories

urlpatterns = [
    path('api/products/', get_products, name='get_products'),
    path('api/products/<int:product_id>/', get_product_by_id, name='get_product_by_id'),
    path('api/products/<int:product_id>/update/', update_product, name='update_product'),
    path('api/products/<int:product_id>/delete/', delete_product, name='delete_product'),
    path('api/products/add/', add_product, name='add_product'),
    path('api/products/categories/', get_product_categories, name='get_product_categories'),


    path('api/moves/', get_moves, name='get_moves'),
    path('api/moves/receipts/', get_receipts, name='get_receipts'),
    path('api/moves/delivery_orders/', get_delivery_orders, name='get_moves'),
]