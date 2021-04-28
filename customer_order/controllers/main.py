import json


from odoo import http
from odoo.http import request

class Products(http.Controller):

    # @http.route(['/api/APiRoute/<int:Var>'], type="http", auth="public", website=True, method=['POST'],
    #             csrf=False)
    @http.route('/customer/order/product/', type="http",website=True, auth="public")
    def order(self, **kw):
        data = request.env['product.details'].sudo().search([])
        print("jkasvbkavbjk ", data)
        # return 'Halo My world'

        return request.render('customer_order.product_page',{
            'product': data
        })

    # def example(self, Var):
        # values = {}
        #
        # data = request.env['ProjectName.TableName'].sudo().search([("id", "=", int(Var))])
        #
        # if data:
        #     values['success'] = True
        #     values['return'] = "Something"
        # else:
        #     values['success'] = False
        #     values['error_code'] = 1
        #     values['error_data'] = 'No data found!'

        # return json.dumps(values)
