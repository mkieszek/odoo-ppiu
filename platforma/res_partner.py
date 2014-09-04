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
    
    def _get_access_partner_search(self, cr, uid, ids, name, arg, context=None):
        val={}
        groups_obj = self.pool.get('res.groups')
        users_obj = self.pool.get('res.users')
        user = users_obj.browse(cr, uid, uid)
        
        group_ids = groups_obj.search(cr, uid, [('name','=','Res Partner Read Partner')])
        child_ids = []
        child_ids.append(user.partner_id.id)
        recomend_ids = self.search(cr, uid, [('partner_recomend','=',True),('id','!=',user.partner_id.id)])

        if group_ids[0] in user.groups_id:
            for recomend in self.browse(cr, uid, recomend_ids):
                parent_ids = self.get_parent_ids(cr, uid, recomend.id)
                if user.partner_id.id in parent_ids:
                    child_ids.append(recomend.id)
        else:
            for recomend_id in recomend_ids:
                child_ids.append(recomend_id)

        if child_ids:
                return [('id', 'in', tuple(child_ids))]
        return [('id', '=', '0')]
    
    _columns = {
        'partner_recomend': fields.boolean('Partner Rekomendujący'),
        'partner_sale': fields.boolean('Partner Handlowy'),
        'sum_points': fields.integer('Punkty prowizji', readonly=True),
        'provision_ppiu': fields.float('Prowizja ze sprzedaży %'),
        'provision_points': fields.function(_get_provision, type='float', string="Poziom prowizyjny %", store=False, readonly=True),
        'access_partner': fields.function(_get_access_partner, type='boolean', string="Blokowanie dla Partnera", store=False, readonly=True, fnct_search=_get_access_partner_search),
        'ppiu_parent_id': fields.many2one('res.partner', 'Partner nadrzędny', domain="[('partner_recomend','=',True),('id','!=',id)]"),
        'ppiu_child_ids': fields.one2many('res.partner', 'ppiu_parent_id', string="Partnerzy podrzędni"),
    }
    
    def create(self, cr, uid, data, context=None):
        partner_id = super(res_partner, self).create(cr, uid, data, context=context)
        
        return partner_id
    
    def get_parent_ids(self, cr, uid, partner_id):
        parent_ids = []
        partner = self.browse(cr, uid, partner_id)
        if partner.ppiu_parent_id:
            parent_ids = self.get_parent_ids(cr, uid, partner.ppiu_parent_id.id)
            parent_ids.append(partner.ppiu_parent_id.id)
            return parent_ids
        else:
            return []