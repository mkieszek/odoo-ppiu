# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
import pdb

POINTS = [('1','5 pkt'),('2','100zł = 1 pkt')]
TYPE = [('consu','Pomocniczy'),('service','Usługa')]

class ppiu_product(osv.Model):
    _name = "ppiu.product"
    _description = 'Product'
    _columns = {
        'name': fields.char('Nazwa produktu', required=True),
        'product_type': fields.selection(TYPE, 'Typ produktu'),
        'is_active': fields.boolean('Aktywny'),
        'points': fields.selection(POINTS, 'Punktacja', required=True),
        'partner_sale_id': fields.many2one('res.partner', 'Partner Handlowy', domain="[('partner_sale','=',True)]", required=True),
        'description': fields.text('Opis'),
        'product_category': fields.many2one('product.category', 'Kategoria produktu'),
        'provision_ppiu': fields.float('Prowizja ze sprzedaży %'),
    }