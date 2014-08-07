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
            points_ids = points_obj.search(cr, uid, [('points_from','<=',points),('points_to','>=',points)])
            point = points_obj.browse(cr, uid, points_ids)
            val[partner.id] = point.provision
        return val
    
    def _get_partner_ids_search(self, cr, uid, ids_i, name, args, context):
        ids = []
        pdb.set_trace()
        return [('id','in',tuple([7,9]))]

    
    def _get_access_partner(self, cr, uid, ids, name, arg, context=None):
        val={}
        groups_obj = self.pool.get('res.groups')
        users_obj = self.pool.get('res.users')
        user = users_obj.browse(cr, uid, uid)
        for partner in self.browse(cr, uid, ids):
            parent_ids = []
            parent_ids = self.get_parent_ids(cr, uid, partner.id)
            group_ids = groups_obj.search(cr, uid, [('name','=','Res Partner Read Partner')])
            if (partner.id == user.partner_id.id or user.partner_id.id in parent_ids) or uid not in group_ids:
                val[partner.id] = False
            else:
                val[partner.id] = True
        return val
    
    def get_parent_ids(self, cr, uid, partner_id):
        parent_ids = []
        partner = self.browse(cr, uid, partner_id)
        if partner.parent_id:
            parent_ids = self.get_parent_ids(cr, uid, partner.parent_id.id)
            parent_ids.append(partner.parent_id.id)
            return parent_ids
        else:
            return []
    
    _columns = {
        'partner': fields.boolean('Partner'),
        'sum_points': fields.integer('Punkty prowizji', readonly=True),
        'provision_ppiu': fields.integer('Prowizje dla PPIU %'),
        'provision_points': fields.function(_get_provision, type='float', string="Poziom prowizji %", store=False, readonly=True),
        'access_partner': fields.function(_get_access_partner, type='boolean', string="Blokowanie dla Partnera", store=False, readonly=True),
        'provision_ppiu_': fields.function(_get_access_partner, type='boolean', string="Blokowanie dla Partnera", store=False, readonly=True),
    }