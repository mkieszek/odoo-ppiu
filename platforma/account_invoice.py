# -*- coding: utf-8 -*-

from openerp.osv.orm import Model
from openerp.osv import fields, osv
import pdb

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    _columns = {
        'lead_ids': fields.one2many('crm.lead', 'account_id', "Lead"),
    }
    
    def create(self, cr, uid, vals, context=None):
        invoice_id = super(account_invoice, self).create(cr, uid, vals, context=context)
        pdb.set_trace()
        lead_obj = self.pool.get('crm.lead')
        if 'lead_ids' in context:
            vals_lead = {
                         'account_id': invoice_id,
                         }
            lead_obj.write(cr, uid, context['lead_ids'], vals_lead, context)
        return invoice_id
    
    def change_state_paid(self, cr, uid, ids, context=None):
        payment_ids = []
        for invoice in self.browse(cr, uid, ids):
            for lead in invoice.lead_ids:
                for payment in lead.payment_ids:
                    payment_ids.append(payment.id)
        if payment_ids:
            self.pool.get('ppiu.payment').write(cr, uid, payment_ids, {'state': '2'})
        return {}
    
class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    
    _columns = {
        'ppiu_product_id':  fields.many2one('ppiu.product', 'Produkt'),
    }