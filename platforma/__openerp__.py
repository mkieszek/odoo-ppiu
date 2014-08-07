# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Platform products and services',
    'version': '0.1',
    'category': 'Products and services',
    'description': """ """,
    'author': 'Via IT Solution',
    'website': 'http://www.viait.pl ',
    'depends': ['crm','product'],
    'data': ['security/security.xml',
             'security/ir.model.access.csv'],
    'demo': [],
    'test':[],
    'installable': True,
    'images': [],
    'update_xml' : [
                    'view/ppiu_sale_points_view.xml',
                    'view/res_partner_view.xml',
                    'view/product_view.xml',
                    'view/ppiu_sale_view.xml',
                    'view/ppiu_payment_view.xml',
                    'view/crm_lead_view.xml',
                    
                    'view/ppiu_menu.xml',
                    ],
    'sequence': 1001,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
# -*- coding: utf-8 -*-