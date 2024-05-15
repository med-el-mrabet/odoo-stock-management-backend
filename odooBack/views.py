import json
import xmlrpc.client
from django.http import JsonResponse

# Connect to Odoo instance
url = 'http://localhost:8069'
db = 'stockmanagement'
username = 'momt20003@gmail.com'
password = 'momt2003'

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))


def get_odoo_data(request):
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