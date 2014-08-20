# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
import pdb

class ppiu_sale(osv.Model):
    _name = "ppiu.sale"
    _inherit = ['mail.thread']
    _description = 'Sale'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner Rekomendujący', domain="[('partner_recomend','=',True)]", required=True),
        'product_id': fields.many2one('product.product', 'Produkt', required=True),
        'value': fields.float('Wartość'),
        #'count_product': fields.integer('Ilość produktu'),
        #'points': fields.related('product_id', 'points', type='integer', string='Punkty za szt.', readonly=True),
        'lead_id': fields.many2one('crm.lead', 'Lead', domain="[('sequence','=',70)]"),
        'payment_ids': fields.one2many('ppiu.payment', 'sale_id', 'Wypłaty'),
    }
    
    def name_get(self, cr, uid, ids, context=None):
        """Overrides orm name_get method"""
        if not isinstance(ids, list) :
            ids = [ids]
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['lead_id', 'partner_id'], context)
        for record in reads:
            lead = ''#record['lead_id'][1]
            partner = record['partner_id'][1]
            res.append((record['id'], lead + ' - ' + partner))
        return res
    
    def create(self, cr, uid, data, context=None):
        if 'lead_id' in data and data['lead_id'] != False:
            lead_obj = self.pool.get('crm.lead')
            lead = lead_obj.browse(cr, uid, data['lead_id'])
            data['partner_id'] = lead.partner_partner_id.id if lead.partner_partner_id != False else False
            data['product_id'] = lead.product_id.id if lead.partner_partner_id != False else False
        sale_id = super(ppiu_sale, self).create(cr, uid, data, context=context)
        sale = self.browse(cr, uid, sale_id)
        partner_obj = self.pool.get('res.partner')
        parent_ids = (partner_obj.get_parent_ids(cr, uid, sale.partner_id.id))
        parent_ids.append(sale.partner_id.id)
        
        for partner in partner_obj.browse(cr, uid, parent_ids):
            payment_vals = {}
            payment_vals = {
                            'partner_id': partner.id,
                            'sale_id': sale_id,
                            'add_points': sale.product_id.points*sale.count_product,
                            }
            self.pool.get('ppiu.payment').create(cr, uid, payment_vals, context=context)
            current_points = partner.sum_points + sale.product_id.points*sale.count_product
            partner_obj.write(cr, uid, [partner.id], {'sum_points': current_points}, context=context)
        
        return sale_id

    def on_change_details(self, cr, uid, ids, lead_id, context=None):
        lead_obj = self.pool.get('crm.lead')
        lead = lead_obj.browse(cr, uid, lead_id)
        value = {}
        value = {
                 'partner_id': lead.partner_partner_id.id,
                 'product_id': lead.product_id.id,
                 }
        
        return {'value':value}