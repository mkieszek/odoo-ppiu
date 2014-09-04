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
    _description = 'Products and services'
    _columns = {
        'name': fields.char('Nazwa produktu / usługi', required=True),
        'product_type': fields.selection(TYPE, 'Typ'),
        'is_active': fields.boolean('Aktywny'),
        'points': fields.selection(POINTS, 'Punktacja', required=True),
        'partner_sale_id': fields.many2one('res.partner', 'Partner Handlowy', domain="[('partner_sale','=',True)]", required=True, groups="platforma.group_ppiu_administration"),
        'description': fields.text('Opis'),
        'product_category': fields.many2one('product.category', 'Kategoria'),
        'provision_ppiu': fields.float('Prowizja ze sprzedaży %', groups="platforma.group_ppiu_administration"),
    }