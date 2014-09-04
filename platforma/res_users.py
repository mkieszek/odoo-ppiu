# -*- coding: utf-8 -*-

from openerp.osv.orm import Model
from openerp.osv import fields, osv
import pdb

class res_users(Model):
    _inherit = "res.users"
    
    _columns = {
    }
    
    def create(self, cr, uid, data, context=None):
        user_id = super(res_users, self).create(cr, uid, data, context=context)
        user = self.browse(cr, uid, user_id)
        
        groups_obj = self.pool.get('res.groups')
        partner_obj = self.pool.get('res.partner')

        if groups_obj.search(cr, uid, [('name','=','Partner Rekomendujący')])[0] in user.groups_id:
            partner_obj.write(cr, uid, [user.partner_id.id], {'partner_recomend':True}, context)
            
        if groups_obj.search(cr, uid, [('name','=','Partner Handlowy')])[0] in user.groups_id:
            partner_obj.write(cr, uid, [user.partner_id.id], {'partner_sale':True}, context)
        return user_id