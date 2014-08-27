# -*- coding: utf-8 -*-
'''
@author: mbereda
'''
from openerp.osv import osv, fields
import datetime
import base64
import pdb

class ppiu_lead2invoice(osv.osv_memory):
    _name = 'ppiu.lead2invoice'
    _description = "Lead to invoice"
    _columns = {
                'name' : fields.char('Name'),
                }
    
    def to_invoice(self, cr, uid, ids, context=None):
        lead_obj = self.pool.get('crm.lead')
        context['lead_ids'] = context['active_ids']
        for lead in lead_obj.browse(cr, uid, context['active_ids']):
            if lead.partner_sale_id:
                context['default_partner_id'] = lead.partner_sale_id.id
                
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr, uid, 'account', 'invoice_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(cr, uid, 'account', 'invoice_tree')
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': 'Invoice',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'account.invoice',
            'res_id': False,
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'type': 'ir.actions.act_window',
            'context': context
        }
        
