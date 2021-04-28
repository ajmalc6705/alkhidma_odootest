
from odoo import fields, models,api,_
import datetime

# Customer Creation
class customercreation(models.Model):

    _name = "custom.details"
    _rec_name = "name"

    name = fields.Char(string="Customer Name")
    c_mob = fields.Char(string='Contact No', size=10)
    c_id = fields.Char('C_ID')
    country_group = fields.Many2one('res.country.group')
    c_state_id = fields.Many2one('res.country.state')
    country_id = fields.Many2one('res.country')
    c_street = fields.Char('Street')
    c_street2 = fields.Char('Street2')
    c_city = fields.Char('City')
    zip = fields.Char('Zip', change_default=True)
    c_vat = fields.Char(string='Tax No.', index=True,
                      help="The Tax Identification Number. Complete it if the contact is subjected to government taxes. Used in some legal statements.")
""" ************************************************************************************************"""
# Product Creation
class product_creation(models.Model):
    _name = "product.details"
    _rec_name = "name"

    name = fields.Char(string='Product Name', required=True)
    image = fields.Binary(string='Product Image')
    currency_id = fields.Many2one('res.currency', string='Currency')
    price = fields.Monetary(string='Sales Price')
    cost_price = fields.Monetary(string='Cost Price')
    expiry_date = fields.Date("Expiration On")

""" *********************************************************************************************************"""
# Sales Order
class sales_order(models.Model):
    _name = 'salesorder.details'

    _description = "Sales Order"
    _rec_name = 'customer_id'
    # To select the  products
    sales_details_line_ids = fields.One2many('sales.order.line', 'reference_id', string ='Sales Order Lines')
    # To Select the Customers
    customer_id = fields.Many2one('custom.details', string='Customer Name')
    date = fields.Datetime(string='Order Date',default=datetime.datetime.now())
    # date = fields.Date(default=(datetime.date.today()))
    contact = fields.Char(compute="onchange_mob_cid")
    street = fields.Char(compute="onchange_mob_cid")
    street2 = fields.Char(compute="onchange_mob_cid")
    zipcode = fields.Char(compute="onchange_mob_cid")
    city = fields.Char(compute="onchange_mob_cid")
    country = fields.Char(compute="onchange_mob_cid")
    cus_id = fields.Char(compute="onchange_mob_cid")
    cus_vat = fields.Char(compute="onchange_mob_cid")
    state = fields.Selection([('draft', 'Draft Quotation'),('confirm', 'Confirmed')], default="draft", string="STATUS")
    # state_button = fields.Selection([('new', 'Draft Quotation'),('confirm', 'Confirm'),('sent', 'Quotation Sent'),
    # ('sale', 'Sales Order'),('done', 'Sales Done'),('cancel', 'Cancelled')], string='STATUS', defualt='draft')
    note = fields.Char()


    # TOTAL AMOUNT ON THE BOTTOM LINE CALCULATION
    sub_total =fields.Float(string='SubTotal',compute='amount_count')
    item_dis = fields.Float(string='ItemDisc', compute='amount_count')
    add_vat = fields.Float(string='Add Vat',compute='amount_count')
    round_off = fields.Float('Round off',compute='amount_count')
    net_total_amount = fields.Float(string='Grand Total', compute='amount_count')

    # """ Taking values from model=sales_details_line_ids"""
    @api.depends('sales_details_line_ids', 'sales_details_line_ids.vat_amount', 'sales_details_line_ids.grand_total')
    def amount_count(self):
        # initialize the record
        for rec in self:
            net_amount = 0.0
            net_disc = 0.0
            net_vat = 0.0
            # roundoff = 0.0
            g_total = 0.0
            n_total = 0.0
            # taking values from sales_details_line_ids
            for line in rec.sales_details_line_ids:
                net_amount += line.grand_total
                net_disc += line.dis
                net_vat += (line.vat_amount)
                g_total += (line.vat_amount + (line.grand_total - line.dis))
                # roundoff += (round(line.vat_amount + (line.grand_total - line.dis))-((line.vat_amount + (line.grand_total - line.dis))))
                n_total += line.grand_total - line.dis+line.vat_amount

            rec.sub_total = net_amount
            rec.item_dis = net_disc
            rec.add_vat = net_vat
            rec.round_off= round(n_total)-n_total
            rec.net_total_amount = round(n_total)

    #total_sales = fields.Float()
    # Confirm state buttons
    def confirm_button_fun(self):
        if not self.state:
            raise Warning('warning')
        else:
            self.state="confirm"
    # Customer Selection Onchange Function
    @api.depends('customer_id')
    def onchange_mob_cid(self):
        for rec in self:
            rec.cus_id=rec.customer_id.c_id
            rec.contact = rec.customer_id.c_mob
            rec.street = rec.customer_id.c_street
            rec.street2 = rec.customer_id.c_street2
            rec.city = rec.customer_id.c_city
            rec.country = rec.customer_id.country_id.name
            rec.zipcode = rec.customer_id.zip
            rec.cus_vat = rec.customer_id.c_vat
        # Another Method
    """# to take customer id and mobile number with respect to customer ID
     @api.depends('customer_id')
     def onchange_mob_cid(self):
         customer_id = self.customer_id and self.customer_id.id
         customer_obj= self.env["custom.details"].browse(customer_id)
         self.cus_id = customer_obj.cid
         self.contact= customer_obj.mob"""


""" ****************************************************************************************************** """
class sales(models.Model):
    _name = 'sales.order.line'
    _rec_name = 'reference_id'

    # reference for One2many of model sales_details_line_ids
    reference_id = fields.Many2one('salesorder.details', string='reference')
    product_id = fields.Many2one('product.details', string='Product Name')
    pro_price = fields.Float()
    qty = fields.Float(string='Qty',default='1.00')
    grand_total = fields.Float(string='GTotal')
    dis_perc = fields.Float('Dis.%100')
    dis = fields.Float('Dis',compute='_amount')
    net_total = fields.Float(string="NetTotal",compute="_amount")
    vat_perc = fields.Float(string='VAT%', default = 5)
    vat_amount = fields.Float(string='VAT amount',compute="_amount")

    # Automatic field entry of product details
    @api.onchange('product_id')
    def _onchange_sale_price(self):
        for rec in self:
            if rec.product_id:
                rec.pro_price=rec.product_id.price

    """def _onchange_sale(self):
        # creating a new ID
        product_id = self.product_id and self.product_id.id
        # creating new object and insert the ID value
        sales_obj = self.env['product.details'].browse(product_id)
        self.pro_price = sales_obj.price"""




    # Sub total calculation
    # @api.depends('qty','pro_price')
    @api.onchange('qty', 'pro_price')
    def _onchange_sub_total(self):
        self.grand_total = (self.qty * self.pro_price)
    # Vat calculation and Total
    @api.depends('grand_total','vat_perc','dis_perc')
    def _amount(self):
        for rec in self:
            rec.dis = round((rec.grand_total*(rec.dis_perc/100)),2)
            rec.vat_amount = round((rec.grand_total*(rec.vat_perc/100)),2)
            rec.net_total = ((rec.grand_total+ rec.vat_amount)-rec.dis)

    # @api.depends('sub_total')
    # def vat_amount(self):
    #     for rec in self:
    #         rec.vat= rec.sub_total*(5/100)
    # # sub Amount Calculation
    # @api.depends('sub_total','vat')
    # def _total_amount(self):
    #     for rec in self:
    #         rec.total = rec.sub_total+rec.vat