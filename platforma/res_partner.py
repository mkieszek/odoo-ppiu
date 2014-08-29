# -*- coding: utf-8 -*-

from openerp.osv.orm import Model
from openerp.osv import fields, osv
import pdb

class res_partner(Model):
    _inherit = "res.partner"
    
    def _get_provision(self, cr, uid, ids, name, arg, context=None):
        val={}
        points_obj = self.pool.get('ppiu.sale.points')
        for partner in self.browse(cr, uid, ids):
            points = partner.sum_points
            val[partner.id] = self._get_provision_p(cr, uid, partner.id, points, context)
        return val
    
    def _get_provision_p(self, cr, uid, partner_id, partner_points, context=None):
        val={}
        points_obj = self.pool.get('ppiu.sale.points')
        partner =  self.browse(cr, uid, partner_id)
        points = partner.sum_points
        points_ids = points_obj.search(cr, uid, [('points_from','<=',points),('points_to','>=',points)])
        point = points_obj.browse(cr, uid, points_ids)
        provision_p = point.provision
        return provision_p
    
    def _get_access_partner(self, cr, uid, ids, name, arg, context=None):
        val={}
        groups_obj = self.pool.get('res.groups')
        users_obj = self.pool.get('res.users')
        user = users_obj.browse(cr, uid, uid)
        for partner in self.browse(cr, uid, ids):
            parent_ids = []
            parent_ids = self.get_parent_ids(cr, uid, partner.id)
            group_ids = groups_obj.search(cr, uid, [('name','=','Res Partner Read Partner')])
            
            if user.partner_id.id != partner.id and group_ids[0] in user.groups_id and user.partner_id.id not in parent_ids:
                val[partner.id] = True
            else:
                val[partner.id] = False
        return val
    
    _columns = {
        'partner_recomend': fields.boolean('Partner Rekomendujący'),
        'partner_sale': fields.boolean('Partner Handlowy'),
        'sum_points': fields.integer('Punkty prowizji', readonly=True),
        'provision_ppiu': fields.float('Prowizje %'),
        'provision_points': fields.function(_get_provision, type='float', string="Poziom prowizyjny %", store=False, readonly=True),
        'access_partner': fields.function(_get_access_partner, type='boolean', string="Blokowanie dla Partnera", store=False, readonly=True),
    }
    
    def get_parent_ids(self, cr, uid, partner_id):
        parent_ids = []
        partner = self.browse(cr, uid, partner_id)
        if partner.parent_id:
            parent_ids = self.get_parent_ids(cr, uid, partner.parent_id.id)
            parent_ids.append(partner.parent_id.id)
            return parent_ids
        else:
            return []