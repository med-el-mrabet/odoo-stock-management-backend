import xmlrpc.client


# Connect to Odoo instance
url = 'http://localhost:8069'
db = 'stockmanagement'
username = 'momt20003@gmail.com'
password = 'momt2003'

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))