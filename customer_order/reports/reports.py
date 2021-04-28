from odoo import fields, models, api


class ModelName(models.Model):
    _name = 'reports.sales'
    _description = 'Sales Report'

    name = fields.Char()
