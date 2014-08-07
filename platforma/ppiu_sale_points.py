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
    }
