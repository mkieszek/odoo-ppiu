# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv

class ppiu_sale_points(osv.Model):
    _name = "ppiu.sale.points"
    _description = 'Sale points'
    _columns = {
    'points_from': fields.integer('Punkty od', required=True),
    'points_to': fields.integer('Punkty do', required=True),
    'provision': fields.float('Prowizja %', required=True),
    'provision_national': fields.float('Prowizja od runku krajowego %', required=True),
    'part_profit': fields.float('Udział w zysku %', required=True),
    'provision_other': fields.float('Prowizja od innych rynktów %', required=True), 
    }
