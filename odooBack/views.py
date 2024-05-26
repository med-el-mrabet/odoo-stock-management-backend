import json
import xmlrpc.client

from django.core.cache import cache
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

# Connect to Odoo instance
url = 'http://localhost:8069'
db = 'stockmanagement'
username = 'momt20003@gmail.com'
password = 'momt2003'

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))


def get_products(request):
    if request.method == 'GET':
        # Fetching products from Odoo
        product_ids = models.execute_kw(db, uid, password, 'product.template', 'search', [[]])
        products = models.execute_kw(db, uid, password, 'product.template', 'read', [product_ids],
                                    {'fields': ['id','default_code', 'name', 'list_price', 'standard_price', 'qty_available',  'outgoing_qty', 'incoming_qty', 'detailed_type']})

        # Serialize data
        serialized_products = [{'id': product['id'], 'name': product['name'], 'list_price': product['list_price'], 'standard_price': product['standard_price'], 'qty_available': product['qty_available'],  'outgoing_qty': product['outgoing_qty'], 'incoming_qty': product['incoming_qty'],'default_code': product['default_code'],'detailed_type': product['detailed_type']} for product in products]

        return JsonResponse(serialized_products, safe=False)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def get_product_by_id(request, product_id):
    if request.method == 'GET':
        # Fetching product by ID from Odoo
        product = models.execute_kw(db, uid, password, 'product.template', 'read', [[product_id]],
                                    {'fields': ['id', 'name', 'list_price']})
        if product:
            return JsonResponse(product[0], safe=False)
        else:
            return JsonResponse({'error': 'Product not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def add_product(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest('Invalid JSON')

        fields = {}
        if 'name' in data:
            fields['name'] = data['name']
        if 'list_price' in data:
            fields['list_price'] = data['list_price']

        if fields:
            try:
                product_id = models.execute_kw(db, uid, password, 'product.template', 'create', [fields])
                cache.delete('products')  # Invalidate the cache for the product list
                return JsonResponse({'success': 'Product added successfully', 'product_id': product_id})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            return JsonResponse({'error': 'No valid fields to create'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def update_product(request, product_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest('Invalid JSON')

        fields = {}
        if 'name' in data:
            fields['name'] = data['name']
        if 'list_price' in data:
            fields['list_price'] = data['list_price']

        if fields:
            models.execute_kw(db, uid, password, 'product.template', 'write', [[product_id], fields])
            return JsonResponse({'success': 'Product updated successfully'})
        else:
            return JsonResponse({'error': 'No valid fields to update'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def delete_product(request, product_id):
    if request.method == 'DELETE':
        models.execute_kw(db, uid, password, 'product.template', 'unlink', [[product_id]])
        return JsonResponse({'success': 'Product deleted successfully'})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt  # Disable CSRF protection for this view
def archive_product(request, product_id):
    if request.method == 'DELETE':
        try:
            # Set the product as inactive instead of deleting
            models.execute_kw(db, uid, password, 'product.template', 'write', [[product_id], {'active': False}])
            cache.delete(f'product_{product_id}')  # Invalidate the cache for the archived product
            cache.delete('products')  # Invalidate the cache for the product list
            return JsonResponse({'success': 'Product archived successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



def get_product_categories(request):
    if request.method == 'GET':
        # Fetching products from Odoo
        categories_ids = models.execute_kw(db, uid, password, 'product.category', 'search', [[]])
        categories = models.execute_kw(db, uid, password, 'product.category', 'read', [categories_ids],
                                    {'fields': ['id', 'name','complete_name','display_name', 'parent_id', 'parent_path', 'child_id', 'create_date',  'property_cost_method']})

        # Serialize data
        serialized_categories = [{'id': categorie['id'], 'name': categorie['name'], 'complete_name': categorie['complete_name'], 'display_name': categorie['display_name'], 'parent_id': categorie['parent_id'],  'parent_path': categorie['parent_path'], 'child_id': categorie['child_id'],'create_date': categorie['create_date'], 'property_cost_method': categorie['property_cost_method']} for categorie in categories]

        return JsonResponse(serialized_categories, safe=False)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)