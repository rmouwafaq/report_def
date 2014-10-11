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

import time
import json
import collections
import os
from report_api import report_api

from openerp.osv import osv, fields

class assistant_report(osv.osv_memory):
    _name = 'report_def.assistant_report'
    _description = 'Assistant Report'

    _columns = {
        'date_start': fields.date('Date Start', required=True),
        'date_end': fields.date('Date End', required=True),
        'user_ids': fields.many2many('res.users', 'report_def_assistant_report_user_rel', 'user_id', 'wizard_id', 'Utilisateur'),
    }
    _defaults = {
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
        'date_end': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def print_report(self, cr, uid, ids, context=None):
        """
         To get the date and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return : retrun report
        """
        if context is None:
            context = {}
            
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date_start', 'date_end', 'user_ids'], context=context)
        
        res = res and res[0] or {}
        datas['form'] = res
        
         
        if res.get('id',False):
            datas['ids']=[res['id']]
            

        rep= report_api()
        result = rep.init_class(cr,uid,self.pool,res,report_name = 'pos_order_detail') 
        return {
            'type' : 'ir.actions.client',
            'name' : 'Report Viewer Action',
            'tag' : 'report.viewer.action',
            'params' : {'report_id': result[0].report.id,'json_id':result[1]},
        }   
         
        #=======================================================================
        # return {
        #    'type': 'ir.actions.report.xml',
        #    'report_name': 'pos.details',
        #    'datas': datas,
        # }
        #=======================================================================

   
         
assistant_report()    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
