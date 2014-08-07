# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv

class ppiu_payment(osv.Model):
    _name = "ppiu.payment"
    _inherit = ['mail.thread']
    _description = 'Payment'
    _columns = {
        'sale_id': fields.many2one('ppiu.sale', 'Sprzedaż'),
        'partner_id': fields.many2one('res.partner', 'Partner', domain="[('partner','=',True)]"),
        'add_points': fields.integer('Dodane punkty'),
        'state': fields.selection((('1', "Do zapłacenia"),('2', 'Zapłacony')), 'Status',  track_visibility='onchange'),
    }
    
    _defaults = {
                 'state': '1',
                 }
    
    def paid(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': '2'})