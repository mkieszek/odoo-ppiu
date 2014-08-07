# -*- coding: utf-8 -*-

from openerp.osv.orm import Model
from openerp.osv import fields, osv
import pdb

class crm_lead(Model):
    _inherit = "crm.lead"
    
    _columns = {
        'partner_partner_id': fields.many2one('res.partner', 'Partner', domain="[('partner','=',True)]"),
        'recom_partner_id': fields.many2one('res.partner', 'Partner polecający', domain="[('partner','=',True)]"),
        'product_id': fields.many2one('product.product', 'Produkt'),
        'sequence': fields.related('stage_id', 'sequence', type='integer', string='Sequence', readonly=True),
    }