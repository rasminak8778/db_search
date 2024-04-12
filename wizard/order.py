from odoo import models, fields
import xmlrpc.client


class CreatedOrders(models.TransientModel):
    _name = 'created.orders'

    from_db_old = fields.Char(string='From Odoo 15')

    to_db_new = fields.Char(string='To Odoo 17')

    def action_fetch_purchase_order(self):
        print('dcre')
        url_db1 = "http://localhost:8015"
        db_1 = 'do15'
        username_db_1 = 'w'
        password_db_1 = 'w'
        common_1 = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/common'.format(url_db1))
        models_1 = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/object'.format(url_db1))
        version_db1 = common_1.version()

        url_db2 = "http://localhost:8017"
        db_2 = 'odo17'
        username_db_2 = 'a'
        password_db_2 = 'a'
        common_2 = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/common'.format(url_db2))
        models_2 = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/object'.format(url_db2))
        version_db2 = common_2.version()
        uid_db1 = common_1.authenticate(db_1, username_db_1, password_db_1, {})
        uid_db2 = common_2.authenticate(db_2, username_db_2, password_db_2, {})
        db_1_purchase_orders = models_1.execute_kw(db_1, uid_db1, password_db_1,
                                                   'purchase.order',
                                                   'search_read', [[('state',
                                                                     '=',
                                                                     'purchase')]],
                                                   {'fields': ['id', 'name',
                                                               'partner_id',
                                                               'amount_total',
                                                               'state',
                                                               'order_line'
                                                               ]})
        print('db_1_purchase_orders', db_1_purchase_orders)

        for rec in db_1_purchase_orders:
            partner_id = models_2.execute_kw(db_2, uid_db2, password_db_2,
                                             'res.partner', 'search',
                                             [[('name', '=',
                                                rec['partner_id'][0])]])
            print('partner_id', partner_id)
            if not partner_id:
                partner_id = models_2.execute_kw(db_2, uid_db2, password_db_2,
                                                 'res.partner', 'create',
                                                 [{'name': rec['partner_id'][
                                                     0]}])
            else:
                partner_id = partner_id[0]
                print('part', partner_id)

                product_ids = []
                for line in rec['order_line']:
                    print('line', line)
                    new = self.env['purchase.order.line'].sudo().browse(line)
                    print('nezzw', new)
                    print(new.product_id, "***************")
                    product_name = new.product_id.name

                    print('product_name', product_name)
                    product_id = models_2.execute_kw(db_2, uid_db2,
                                                     password_db_2,
                                                     'product.product',
                                                     'search',
                                                     [[('name', '=',
                                                        product_name)]])
                    if not product_id:
                        product_id = models_2.execute_kw(db_2, uid_db2,
                                                         password_db_2,
                                                         'product.product',
                                                         'create',
                                                         [{
                                                             'name': product_name}])
                    else:
                        product_id = product_id[0]
                    product_ids.append((0, 0, {'product_id': product_id,
                                               'name': line['name'],
                                               'price_unit': line['price_unit'],
                                               'product_qty': line[
                                                   'product_qty']}))
                added_purchase_order = models_2.execute_kw(db_2, uid_db2,
                                                           password_db_2,
                                                           'purchase.order',
                                                           'create', [{'name':
                                                                           rec[
                                                                               'name'],
                                                                       'partner_id': partner_id,
                                                                       'date_order':
                                                                           rec[
                                                                               'date_order'],
                                                                       'amount_total':
                                                                           rec[
                                                                               'amount_total'],
                                                                       'state':
                                                                           rec[
                                                                               'state'],
                                                                       'order_line': product_ids}])
                print('added_purchase_order', added_purchase_order)
