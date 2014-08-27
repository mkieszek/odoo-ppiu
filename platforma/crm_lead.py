# -*- coding: utf-8 -*-

from openerp.osv.orm import Model
from openerp.osv import fields, osv
import pdb

class crm_lead(Model):
    _inherit = "crm.lead"
    
    def _get_provision(self, cr, uid, ids, name, arg, context=None):
        val={}
        for lead in self.browse(cr, uid, ids):
            val[lead.id] = lead.value*(lead.provision_p/100)
        return val
    
    _columns = {
        'partner_sale_id': fields.many2one('res.partner', 'Partner handlowy', domain="[('partner_sale','=',True)]"),
        'recom_partner_id': fields.many2one('res.partner', 'Partner polecający', domain="[('partner_recomend','=',True)]"),
        'product_id': fields.many2one('ppiu.product', 'Produkt', domain="[('active','=',True)]"),
        'sequence': fields.related('stage_id', 'sequence', type='integer', string='Sequence', readonly=True),
        'payment_ids': fields.one2many('ppiu.payment', 'lead_id', 'Wypłaty'),
        'sale_date': fields.date('Data sprzedaży'),
        'provision_p': fields.float('Prowizja 30%', readonly=True),
        'provision': fields.function(_get_provision, type='float', string="Prowizja", store=False, readonly=True),
        'value': fields.float('Wartość'),
        'account_id': fields.many2one('account.invoice', 'Faktura'),
    }
    
    _defaults = {
                 'provision_p': 30.0,
                 }
    
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
        payment_obj.create(cr, uid, payment_value)
        if partner.parent_id:
            amount = 0.0
            amount = provision*((partner.parent_id.provision_points-partner.provision_points)/100)
            parent_ids = self.create_payment(cr, uid, partner.parent_id.id, lead_id, points, provision, amount)
            
        