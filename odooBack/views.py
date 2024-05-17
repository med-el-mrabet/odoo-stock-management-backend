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
                                     {'fields': ['id', 'name', 'list_price']})

        # Serialize data
        serialized_products = [{'id': product['id'], 'name': product['name'], 'list_price': product['list_price']} for
                               product in products]

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
