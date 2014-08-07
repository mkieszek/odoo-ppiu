# -*- coding: utf-8 -*-

from openerp.osv.orm import Model
from openerp.osv import fields

class product_product(Model):
    _inherit = "product.product"
    
    _columns = {
        'points': fields.integer('Wartość punktowa'),
        'circs': fields.integer('Warunki handlowe %'),
    }