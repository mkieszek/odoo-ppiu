# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv

class ppiu_payment(osv.Model):
    _name = "ppiu.payment"
    _inherit = ['mail.thread']
    _description = 'Payment'
    _rec_name = "partner_id"
    
    _columns = {
        'lead_id': fields.many2one('crm.lead', 'Szansa'),
        'partner_id': fields.many2one('res.partner', 'Partner', domain="[('partner','=',True)]"),
        'add_points': fields.integer('Dodane punkty'),
        'state': fields.selection((('1', "Do zapłacenia"),('2','W trakcie'),('3', 'Zapłacony')), 'Status',  track_visibility='onchange'),
        'amount': fields.float('Kwota'),
    }
    
    _defaults = {
                 'state': '1',
                 }
    
    def in_progress(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': '2'})
    
    def paid(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': '3'})