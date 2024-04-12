{
    'name': 'DB Purchase Order',
    'version': '17.0.1.0.0',
    'description': 'Fetch Odoo 15 created Purchase order into Odoo 17',
    'category': 'CRM/CRM Dashboard',
    'summary': 'Fetch Odoo 15 created Purchase order into Odoo 17',
    'installable': True,
    'application': True,
    'depends': [
        'purchase',
        'base',
        'sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_order_views.xml',
        'views/purchase_menu.xml',
    ],

}
