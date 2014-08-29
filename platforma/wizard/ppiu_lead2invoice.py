# -*- coding: utf-8 -*-
'''
@author: mbereda
'''
from openerp.osv import osv, fields
from openerp.addons.mail.mail_message import decode
import datetime
import base64
import pdb

class ppiu_lead2invoice(osv.osv_memory):
    _name = 'ppiu.lead2invoice'
    _description = "Lead to invoice"
    _columns = {
                'name' : fields.char('Name'),
                'lead_ids': fields.many2many('crm.lead', string='Szanse'),
                }
    def default_get(self, cr, uid, ids, context=None):
        """
        This function gets default values
        """
        res = super(ppiu_lead2invoice, self).default_get(cr, uid, ids, context=context)
        ids = context and context.get('active_id', False) or False
        lead_ids = context and context.get('active_ids', False) or False
        
        res.update({'lead_ids': self.get_lead_to_invoice(cr, uid, lead_ids)})
        
        return res
    
    def to_invoice(self, cr, uid, ids, context=None):
        lead_obj = self.pool.get('crm.lead')
        context['lead_ids'] = self.get_lead_to_invoice(cr, uid, context['active_ids'])
        if not context['lead_ids']:
            raise osv.except_osv(decode('Ostrzeżenie'), decode('Nie wybrano właściwych szans'))
        for lead in lead_obj.browse(cr, uid, context['lead_ids']):
            if lead.partner_sale_id:
                context['default_partner_id'] = lead.partner_sale_id.id
                
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr, uid, 'account', 'invoice_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(cr, uid, 'account', 'invoice_tree')
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': 'Faktura',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'account.invoice',
            'res_id': False,
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'type': 'ir.actions.act_window',
            'context': context
        }
        
    def get_lead_to_invoice(self, cr, uid, lead_ids):
        lead_obj = self.pool.get('crm.lead')
        
        for lead in lead_obj.browse(cr, uid, lead_ids):
            if lead.account_id or lead.sequence != 70:
                del lead_ids[lead_ids.index(lead.id)]
        
        return lead_ids
