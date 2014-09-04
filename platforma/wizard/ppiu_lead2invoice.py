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
        
        invoice_lines = []
        pdb.set_trace()
        for lead in lead_obj.browse(cr, uid, context['lead_ids']):
            if lead.partner_sale_id:
                context['default_partner_id'] = lead.partner_sale_id.id
                #context['default_invoice_line'] = [[0, False, {'name': 'cod'}]]
            invoice_line = {
                            'name': lead.name,
                            'ppiu_product_id': lead.product_id.id,
                            'price_unit': lead.provision
                            }
            invoice_lines.append([0, False, invoice_line])
            
        if 'default_partner_id' in context:
            context['default_invoice_line'] = invoice_lines
                
        """
        'invoice_line': [[0,
                   False,
                   {'account_analytic_id': False,
                    'account_id': 266,
                    'discount': 0,
                    'invoice_id': 1,
                    'invoice_line_gross': 0,
                    'invoice_line_tax': 0,
                    'invoice_line_tax_id': [[6, False, []]],
                    'name': 'cos',
                    'ppiu_product_id': 1,
                    'price_unit': 15,
                    'product_id': False,
                    'quantity': 1,
                    'uos_id': False}]],
        """
                
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
