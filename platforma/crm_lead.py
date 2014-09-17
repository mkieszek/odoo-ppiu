# -*- coding: utf-8 -*-

from openerp.osv.orm import Model
from openerp.osv import fields, osv
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.http import request
import pytz
import pdb

class crm_lead(Model):
    _inherit = "crm.lead"
    
    def _get_provision(self, cr, uid, ids, name, arg, context=None):
        val={}
        for lead in self.browse(cr, uid, ids):
            val[lead.id] = lead.provision_value*(lead.provision_p/100)
        return val
    
    def _get_str_partner_ids(self, cr, uid, ids, name, arg, context=None):
        val={}
        user_obj = self.pool.get('res.users')
        user_ids = user_obj.search(cr,uid,[('groups_id.name','=','Administracja'),('id','!=',1)])
        for lead in self.browse(cr, uid, ids):
            val[lead.id] = (''.join(str(user.partner_id.id)+',' for user in user_obj.browse(cr, uid ,user_ids)))[:-1]
        return val
    
    def get_date_formats(self, cr, uid, context):
        lang = context.get("lang")
        res_lang = self.pool.get('res.lang')
        lang_params = {}
        if lang:
            ids = res_lang.search(request.cr, uid, [("code", "=", lang)])
            if ids:
                lang_params = res_lang.read(request.cr, uid, ids[0], ["date_format", "time_format"])
        format_date = lang_params.get("date_format", '%B-%d-%Y')
        format_time = lang_params.get("time_format", '%I-%M %p')
        return (format_date, format_time)
    
    def get_interval(self, cr, uid, ids, date, interval, tz=None, context=None):
        #Function used only in calendar_event_data.xml for email template
        date = datetime.strptime(date.split('.')[0], DEFAULT_SERVER_DATETIME_FORMAT)

        if tz:
            timezone = pytz.timezone(tz or 'UTC')
            date = date.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)

        if interval == 'day':
            res = str(date.day)
        elif interval == 'month':
            res = date.strftime('%B') + " " + str(date.year)
        elif interval == 'dayname':
            res = date.strftime('%A')
        elif interval == 'time':
            dummy, format_time = self.get_date_formats(cr, uid, context=context)
            res = date.strftime(format_time + " %Z")
        elif interval == 'datetime':
            dummy, format_time = self.get_date_formats(cr, uid, context=context)
            res = date.strftime(dummy)+' '+date.strftime(format_time)
        return res
    
    _columns = {
        'partner_sale_id': fields.many2one('res.partner', 'Partner handlowy', domain="[('partner_sale','=',True)]"),
        'product_id': fields.many2one('ppiu.product', 'Produkt', domain="[('is_active','=',True)]"),
        'sequence': fields.related('stage_id', 'sequence', type='integer', string='Sequence', readonly=True),
        'payment_ids': fields.one2many('ppiu.payment', 'lead_id', 'Wypłaty'),
        'sale_date': fields.date('Data sprzedaży'),
        'provision_p': fields.float('Prowizja 30% invisible', readonly=True),
        'provision': fields.function(_get_provision, type='float', string="Prowizja 30%", store=False, readonly=True),
        'value': fields.float('Wartość sprzedaży'),
        'provision_value': fields.float('Prowizja PPiU'),
        'account_id': fields.many2one('account.invoice', 'Faktura'),
        'str_partner_ids': fields.function(_get_str_partner_ids, type='char', string="Partners", store=False, readonly=True),
    }
    
    _defaults = {
                 'provision_p': 30.0,
                 }
    
    def create(self, cr, uid, data, context=None):
        lead_id = super(crm_lead, self).create(cr, uid, data, context=context)
        admin_ppiu_ids = []
        user_obj = self.pool.get('res.users')
        user_ids = user_obj.search(cr,uid,[('groups_id.name','=','Administracja'),('id','!=',1)])
        for user in user_obj.browse(cr, uid, user_ids):
            admin_ppiu_ids.append(user.partner_id.id)
            
        if admin_ppiu_ids and data['type'] == 'lead':
            self.message_subscribe(cr, uid, [lead_id], admin_ppiu_ids, context=context)
            self.create_lead_email(cr, uid, lead_id, context)
            
        if 'partner_sale_id' in data and data['partner_sale_id'] and self.pool.get('res.users').browse(cr, uid, data['partner_sale_id']).email:
            for id in ids:
                self.partner_to_oppor_email(cr, uid, id, context)
        return lead_id
    
    def write(self, cr, uid, ids, data, context=None):
        lead_id = super(crm_lead, self).write(cr, uid, ids, data, context=context)
        if 'partner_sale_id' in data and data['partner_sale_id'] and self.pool.get('res.users').browse(cr, uid, data['partner_sale_id']).email:
            for id in ids:
                self.partner_to_oppor_email(cr, uid, id, context)
        return lead_id
    
    def create_lead_email(self, cr, uid, id, context=None):
        template = self.pool.get('ir.model.data').get_object(cr, uid, 'platforma', 'crm_lead_create_email')
        self.pool.get('email.template').send_mail(cr, uid, template.id, id, force_send=True, raise_exception=True, context=context)
        return True
    
    def partner_to_oppor_email(self, cr, uid, id, context=None):
        template = self.pool.get('ir.model.data').get_object(cr, uid, 'platforma', 'crm_lead_to_oppor_email')
        self.pool.get('email.template').send_mail(cr, uid, template.id, id, force_send=True, raise_exception=True, context=context)
        return True
    
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
            amount = lead.provision+lead.provision_value*(partner.provision_points/100)
            self.create_payment(cr, uid, partner.id, ids[0], points, lead.provision_value, amount)
            
        elif lead.user_id.partner_id and lead.user_id.partner_id == lead.partner_id:
            partner = lead.user_id.partner_id
            amount = 0.0
            amount = lead.provision+lead.provision_value*(partner.provision_points/100)
            self.create_payment(cr, uid, partner.id, ids[0], points, lead.provision_value, amount)
            
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
            amount = lead.provision_value*(partner.provision_points/100)
            self.create_payment(cr, uid, partner.id, ids[0], points, lead.provision_value, amount)
        return True
    
    def create_payment(self, cr, uid, partner_id, lead_id, points, provision_value, amount):
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
        
        if partner.ppiu_parent_id:
            amount = 0.0
            amount = provision_value*((partner.ppiu_parent_id.provision_points-partner_obj._get_provision_p(cr, uid, partner.id, partner.sum_points-points))/100)
            parent_ids = self.create_payment(cr, uid, partner.ppiu_parent_id.id, lead_id, points, provision_value, amount)
            
        