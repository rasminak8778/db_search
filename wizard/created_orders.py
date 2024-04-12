from odoo import models, fields
import xmlrpc.client
from odoo.exceptions import ValidationError


class CreatedOrders(models.TransientModel):
    _name = 'created.orders'

    from_db_old = fields.Char(string='From Odoo 15', default='Odoo 15',
                              readonly=True)
    to_db_new = fields.Char(string='To Odoo 17', default='Odoo 17',
                            readonly=True)
    current_db_name = fields.Char(string='Current database Name',
                                  help='17po', default=lambda self: self.env
                                  .cr.dbname)
    old_db_name = fields.Char(string='Old database Name',
                              help='do15')
    old_db_password = fields.Char(string='Old database Password', help='w')
    current_db_user_name = fields.Char(string='Current database User Name',
                                       help='17')
    current_db_password = fields.Char(string='Current database Password',
                                      help='17')
    old_db_user_name = fields.Char(string='Old database User Name',
                                   help='w')
    old_port_no = fields.Char(string='Old port Number',
                              help='Old port Number', default='8015')
    current_port_no = fields.Char(string='Current port Number',
                                  help='Current port Number', default='8017')

    def action_fetch_purchase_order(self):
        """function for fetching data from odoo 15 db to odoo 17"""
        if self.current_db_name != '17po' and self.old_db_name != 'do15':
            raise ValidationError("Mismatch in DataBase Name")
        url_db1 = "http://localhost:8015"
        db_1 = 'do15'
        username_db_1 = self.old_db_user_name
        password_db_1 = self.old_db_password
        common_1 = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/common'.format(url_db1))
        models_1 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.
                                             format(url_db1))
        version_db1 = common_1.version()

        url_db2 = "http://localhost:8017"
        db_2 = '17po'
        username_db_2 = self.current_db_user_name
        password_db_2 = self.current_db_password
        common_2 = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/common'.format(url_db2))
        models_2 = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/object'.format(url_db2))
        version_db2 = common_2.version()
        uid_db1 = common_1.authenticate(db_1, username_db_1, password_db_1, {})
        uid_db2 = common_2.authenticate(db_2, username_db_2, password_db_2, {})


        db_1_partners = models_1.execute_kw(db_1, uid_db1, password_db_1,
                                            'res.partner',
                                            'search_read', [[]],
                                            {'fields': ['id', 'name', 'email',
                                                        'display_name']})

        partners = self.env['res.partner'].search([]).mapped('name')
        partner_details = []
        for record in db_1_partners:
            if record['name'] not in partners:
                partner_details.append(record)
        new_partners = models_2.execute_kw(db_2, uid_db2, password_db_2,
                                           'res.partner',
                                           'create', [partner_details])
        db_1_products = models_1.execute_kw(db_1, uid_db1, password_db_1,
                                            'product.template',
                                            'search_read', [[]],
                                            {'fields': ['id', 'name']})
        products = self.env['product.template'].search([]).mapped('name')
        product_details = []
        for record in db_1_products:
            if record['name'] not in products:
                product_details.append(record)
        new_products = models_2.execute_kw(db_2, uid_db2, password_db_2,
                                           'product.template',
                                           'create', [product_details])
        db_1_po = models_1.execute_kw(db_1, uid_db1, password_db_1,
                                      'purchase.order',
                                      'search_read',
                                      [[]],
                                      {'fields': ['id', 'name', 'date_order',
                                                  'partner_id']})
        purchases = self.env['purchase.order'].search([]).mapped('name')
        db_po_details = []
        for record in db_1_po:
            if record['name'] not in purchases:
                partner_id = self.env['res.partner'].search(
                    [('name', '=', record['partner_id'][1])]).id
                print('partner_id', partner_id)
                record = {
                    'id': record['id'],
                    'name': record['name'],
                    'partner_id': partner_id
                }
                db_po_details.append(record)
        new_po = models_2.execute_kw(db_2, uid_db2, password_db_2,
                                     'purchase.order',
                                     'create', [db_po_details])
        db_1_po_lines = models_1.execute_kw(db_1, uid_db1, password_db_1,
                                            'purchase.order.line',
                                            'search_read',
                                            [[]],
                                            {'fields': ['id', 'name',
                                                        'product_qty',
                                                        'product_id',
                                                        'price_unit',
                                                        'price_subtotal',
                                                        'price_total',
                                                        'order_id']})
        purchase_lines = self.env['purchase.order.line'].search([])
        po_lines_d = []
        for po in self.env['purchase.order'].search([]).mapped('name'):
            for line in db_1_po_lines:
                if line['order_id'][1] == po:
                    product_name_list = line['product_id'][1].split('] ')
                    if len(product_name_list) == 1:
                        product_name = product_name_list[0]
                    else:
                        product_name = product_name_list[1]
                    product_tmpl_id = self.env['product.template'].search(
                        [('name', '=', product_name)]).id
                    product_id = self.env['product.product'].search(
                        [('product_tmpl_id', '=', product_tmpl_id)]).id
                    order_id = self.env['purchase.order'].search(
                        [('name', '=', line['order_id'][1])]).id
                    if product_name not in purchase_lines.mapped(
                            'name') and order_id not in purchase_lines.mapped(
                            'order_id.id'):
                        record = {
                            'id': line['id'],
                            'name': product_name,
                            'product_id': product_id,
                            'product_qty': line['product_qty'],
                            'price_unit': line['price_unit'],
                            'price_subtotal': line['price_subtotal'],
                            'price_total': line['price_total'],
                            'order_id': order_id
                        }

                        po_lines_d.append(record)
                        new_po_lines = models_2.execute_kw(db_2, uid_db2,
                                                           password_db_2,
                                                           'purchase.order.line'
                                                           , 'create',
                                                           [po_lines_d])
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Data Fetched Successfully',
                'type': 'rainbow_man',
            }
        }
