# -*- coding: utf-8 -*-

from openerp.osv.orm import Model
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID, models
import pdb

class res_users(Model):
    _inherit = "res.users"
    
    def _get_group(self,cr, uid, context=None):
        dataobj = self.pool.get('ir.model.data')
        result = []
        try:
            dummy,group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_user')
            result.append(group_id)
        except ValueError:
            # If these groups does not exists anymore
            pass
        return result
    
    _columns = {
    }
    
    _defaults = {
                 'groups_id': _get_group,
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
    