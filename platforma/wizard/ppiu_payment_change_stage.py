# -*- coding: utf-8 -*-
'''
@author: mbereda
'''
from openerp.osv import osv, fields
from openerp.addons.mail.mail_message import decode
import datetime
import base64
import pdb

class ppiu_payment_change_stage(osv.osv_memory):
    _name = 'ppiu.payment.change.stage'
    _description = "Payment change stage"
    _columns = {
                'name' : fields.char('Name'),
                'payment_ids': fields.many2many('ppiu.payment', string='Wypłaty'),
                }
    def default_get(self, cr, uid, ids, context=None):
        """
        This function gets default values
        """
        res = super(ppiu_payment_change_stage, self).default_get(cr, uid, ids, context=context)
        ids = context and context.get('active_id', False) or False
        payment_ids = context and context.get('active_ids', False) or False
        for payment in self.pool.get('ppiu.payment').browse(cr, uid, payment_ids):
            if payment.state == '3':
                del payment_ids[payment_ids.index(payment.id)]
        
        res.update({'payment_ids': payment_ids})
        
        return res
    
    def payment(self, cr, uid, ids, context=None):
        payment_ids = context and context.get('active_ids', False) or False
        self.pool.get('ppiu.payment').write(cr, uid, payment_ids, {'state': '3'})