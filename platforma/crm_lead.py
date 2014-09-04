# -*- coding: utf-8 -*-

from openerp.osv.orm import Model
from openerp.osv import fields, osv
import pdb

class crm_lead(Model):
    _inherit = "crm.lead"
    
    def _get_provision(self, cr, uid, ids, name, arg, context=None):
        val={}
        for lead in self.browse(cr, uid, ids):
            val[lead.id] = lead.provision_value*(lead.provision_p/100)
        return val
    
    _columns = {
        'partner_sale_id': fields.many2one('res.partner', 'Partner handlowy', domain="[('partner_sale','=',True)]"),
        'recom_partner_id': fields.many2one('res.partner', 'Partner polecający', domain="[('partner_recomend','=',True)]"),
        'product_id': fields.many2one('ppiu.product', 'Produkt', domain="[('is_active','=',True)]"),
        'sequence': fields.related('stage_id', 'sequence', type='integer', string='Sequence', readonly=True),
        'payment_ids': fields.one2many('ppiu.payment', 'lead_id', 'Wypłaty'),
        'sale_date': fields.date('Data sprzedaży'),
        'provision_p': fields.float('Prowizja 30% invisible', readonly=True),
        'provision': fields.function(_get_provision, type='float', string="Prowizja 30%", store=False, readonly=True),
        'value': fields.float('Wartość sprzedaży'),
        'provision_value': fields.float('Prowizja PPiU'),
        'account_id': fields.many2one('account.invoice', 'Faktura'),
    }
    
    _defaults = {
                 'provision_p': 30.0,
                 }
    
    def on_change_provision_ppiu(self, cr, uid, ids, product_id, partner_sale_id, amount, context=None):
        vals = {}
        if product_id and partner_sale_id and amount and amount != 0:
            vals['provision_value'] = self.get_provision_ppiu(cr, uid, product_id, partner_sale_id, amount)
        else:
            vals['provision_value'] = 0.0
        
        return {'value': vals}
    
    def get_provision_ppiu(self, cr, uid, product_id, partner_sale_id, value):
        product = self.pool.get('ppiu.product').browse(cr, uid, product_id)
        partner_sale = self.pool.get('res.partner').browse(cr, uid, partner_sale_id)
        amount = 0.0
        if product.provision_ppiu and product.provision_ppiu != 0.0:
            amount = value*(product.provision_ppiu/100)
        elif partner_sale.provision_ppiu and partner_sale.provision_ppiu != 0.0:
            amount = value*(partner_sale.provision_ppiu/100)
        return amount
    
    def get_payment(self, cr, uid, ids, context=None):
        lead = self.browse(cr, uid, ids[0])
        points = 5
        if lead.product_id.points != '1':
            points = round(lead.value/100)

        if lead.user_id.partner_id and lead.user_id.partner_id != lead.partner_id and not lead.partner_id.partner_recomend:
            partner = lead.user_id.partner_id
            amount = 0.0
            amount = lead.provision+lead.provision*(partner.provision_points/100)
            self.create_payment(cr, uid, partner.id, ids[0], points, lead.provision, amount)
            
        elif lead.user_id.partner_id and lead.user_id.partner_id == lead.partner_id:
            partner = lead.user_id.partner_id
            amount = 0.0
            amount = lead.provision+lead.provision*(partner.provision_points/100)
            self.create_payment(cr, uid, partner.id, ids[0], points, lead.provision, amount)
            
        elif lead.user_id.partner_id and lead.user_id.partner_id != lead.partner_id and lead.partner_id.partner_recomend:
            payment_value = {}
            payment_value = {
                             'lead_id': lead.id,
                             'partner_id': lead.partner_id.id,
                             'add_points': points,
                             'state': '1',
                             'amount': lead.provision,
                             }
            self.pool.get('ppiu.payment').create(cr, uid, payment_value)
            partner = lead.user_id.partner_id
            amount = 0.0
            amount = lead.provision*(partner.provision_points/100)
            self.create_payment(cr, uid, partner.id, ids[0], points, lead.provision, amount)
        return True
    
    def create_payment(self, cr, uid, partner_id, lead_id, points, provision, amount):
        payment_obj = self.pool.get('ppiu.payment')
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, partner_id)
        payment_value = {}
        payment_value = {
                         'lead_id': lead_id,
                         'partner_id': partner_id,
                         'add_points': points,
                         'state': '1',
                         'amount': amount,
                         }
        if amount != 0.0:
            payment_obj.create(cr, uid, payment_value)
        partner_points = partner.sum_points + points
        partner_obj.write(cr, uid, [partner.id], {'sum_points': partner_points})
        
        if partner.parent_id:
            amount = 0.0
            amount = provision*((partner.parent_id.provision_points-partner_obj._get_provision_p(cr, uid, partner.id, partner.sum_points-points))/100)
            parent_ids = self.create_payment(cr, uid, partner.parent_id.id, lead_id, points, provision, amount)
            
        