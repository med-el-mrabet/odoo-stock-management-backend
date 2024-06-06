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


# Fetching products from Odoo
product_ids = models.execute_kw(db, uid, password, 'product.template', 'search', [[]])
products = models.execute_kw(db, uid, password, 'product.template', 'read', [product_ids])

@csrf_exempt
def get_products(request):
    if request.method == 'GET':
        return JsonResponse(products, safe=False)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def get_product_by_id(request, product_id):
    if request.method == 'GET':
        # Fetching product by ID from Odoo
        product = models.execute_kw(db, uid, password, 'product.template', 'read', [[product_id]])
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
            # Set fields that are allowed during creation
            product_data = {
                'name': data.get('name'),
                'default_code': data.get('default_code'),
                'list_price': data.get('list_price'),
                'standard_price': data.get('standard_price'),
                'categ_id': data.get('categ_id', 1),
                'detailed_type': data.get('detailed_type', 'product'),  # default to 'product'
                'sale_ok': data.get('sale_ok', True),
                'purchase_ok': data.get('purchase_ok', True),
            }
            print(product_data)
            product_id = models.execute_kw(db, uid, password, 'product.template', 'create', [product_data])
            return JsonResponse({'product_id': product_id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


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
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
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

# Fetching products from Odoo
categories_ids = models.execute_kw(db, uid, password, 'product.category', 'search', [[]])
categories = models.execute_kw(db, uid, password, 'product.category', 'read', [categories_ids],
                                    {'fields': ['id', 'name','complete_name','display_name', 'parent_id', 'parent_path', 'child_id', 'create_date',  'property_cost_method']})

        # Serialize data
serialized_categories = [{'id': categorie['id'], 'name': categorie['name'], 'complete_name': categorie['complete_name'], 'display_name': categorie['display_name'], 'parent_id': categorie['parent_id'],  'parent_path': categorie['parent_path'], 'child_id': categorie['child_id'],'create_date': categorie['create_date'], 'property_cost_method': categorie['property_cost_method']} for categorie in categories]

@csrf_exempt
def get_product_categories(request):
    if request.method == 'GET':
        
        return JsonResponse(serialized_categories, safe=False)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)





@csrf_exempt
def get_moves(request):
    if request.method == 'GET':
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        move_ids = models.execute_kw(db, uid, password, 'stock.move', 'search', [[]])
        moves = models.execute_kw(db, uid, password, 'stock.move', 'read', [move_ids])
        return JsonResponse(moves, safe=False)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def get_move_by_id(request, move_id):
    if request.method == 'GET':
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        move = models.execute_kw(db, uid, password, 'stock.picking', 'read', [[move_id]])
        if move:
            return JsonResponse(move[0], safe=False)
        else:
            return JsonResponse({'error': 'Product not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def get_moves_by_ids(request):
    if request.method == 'GET':
        # Extract IDs from request parameters
        ids = request.GET.getlist('ids')
        if not ids:
            return JsonResponse({'error': 'No IDs provided'}, status=400)
        
        try:
            ids = list(map(int, ids))  # Convert to list of integers
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

            # Fetch the moves by IDs
            moves = models.execute_kw(db, uid, password, 'stock.move', 'read', [ids])
            if moves:
                return JsonResponse(moves, safe=False)
            else:
                return JsonResponse({'error': 'No moves found for the provided IDs'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



@csrf_exempt
def get_pickings(request):
    if request.method == 'GET':
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        pickings_ids = models.execute_kw(db, uid, password, 'stock.picking', 'search', [[]])
        pickings = models.execute_kw(db, uid, password, 'stock.picking', 'read', [pickings_ids])
        return JsonResponse(pickings, safe=False)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    




@csrf_exempt
def get_receipts(request):
    if request.method == 'GET':
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        pickings_ids = models.execute_kw(db, uid, password, 'stock.picking', 'search', [[]])
        pickings = models.execute_kw(db, uid, password, 'stock.picking', 'read', [pickings_ids])
        receipts = [move for move in pickings if move['picking_type_id'][0] == 1]
        
        return JsonResponse(receipts, safe=False)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    

@csrf_exempt
def get_delivery_orders(request):
    if request.method == 'GET':
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        pickings_ids = models.execute_kw(db, uid, password, 'stock.picking', 'search', [[]])
        pickings = models.execute_kw(db, uid, password, 'stock.picking', 'read', [pickings_ids])
        delivery_orders = [picking for picking in pickings if picking['picking_type_id'][0] == 2]        
        return JsonResponse(delivery_orders, safe=False)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
@csrf_exempt
def get_pickings_by_id(request, pick_id):
    if request.method == 'GET':
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        pick = models.execute_kw(db, uid, password, 'stock.picking', 'read', [[pick_id]])
        if pick:
            return JsonResponse(pick[0], safe=False)
        else:
            return JsonResponse({'error': 'Product not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    

@csrf_exempt
def change_pickings_order_state(request, order_id, new_state):
    if request.method == 'POST':
        try:
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

            if new_state not in ['confirmed', 'done', 'cancel']:
                return JsonResponse({'error': 'Invalid state'}, status=400)

            # Fetch the delivery order by ID
            delivery_order = models.execute_kw(db, uid, password, 'stock.picking', 'read', [[order_id]])
            if not delivery_order:
                return JsonResponse({'error': 'Delivery order not found'}, status=404)

            # Call the appropriate method based on the desired state
            if new_state == 'confirmed':
                models.execute_kw(db, uid, password, 'stock.picking', 'action_confirm', [[order_id]])
            elif new_state == 'done':
                models.execute_kw(db, uid, password, 'stock.picking', 'button_validate', [[order_id]])
            elif new_state == 'cancel':
                models.execute_kw(db, uid, password, 'stock.picking', 'action_cancel', [[order_id]])

            return JsonResponse({'message': 'State updated successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)