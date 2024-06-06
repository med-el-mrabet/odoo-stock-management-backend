from django.urls import path
from .views import get_products,get_move_by_id, get_pickings, get_moves, change_pickings_order_state, get_moves, get_delivery_orders, get_pickings_by_id, get_receipts, get_product_by_id, update_product, delete_product, add_product, get_product_categories, get_moves_by_ids

urlpatterns = [
    path('api/products/', get_products, name='get_products'),
    path('api/products/<int:product_id>/', get_product_by_id, name='get_product_by_id'),
    path('api/products/<int:product_id>/update/', update_product, name='update_product'),
    path('api/products/<int:product_id>/delete/', delete_product, name='delete_product'),
    path('api/products/add/', add_product, name='add_product'),
    path('api/products/categories/', get_product_categories, name='get_product_categories'),


    path('api/pickings/', get_pickings, name='get_moves'),
    path('api/pickings/<int:pick_id>/', get_pickings_by_id, name='get_pickings_by_id'),

    path('api/moves/', get_moves, name='get_movess'),
    path('api/moves/<int:move_id>/', get_move_by_id, name='get_move_by_id'),
    path('api/moves_by_ids/', get_moves_by_ids, name='get_moves_by_ids'),

    path('api/pickings/receipts/', get_receipts, name='get_receipts'),

    path('api/pickings/delivery_orders/', get_delivery_orders, name='get_delivery_orders'),
    path('api/pickings/pickings/<int:order_id>/<str:new_state>/', change_pickings_order_state, name='change_pickings_order_state'),
    
]