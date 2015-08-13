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
import os
import time
from openerp.tools.translate import _
from openerp.addons.ao_basic_module import ao_register
from agilreport.Agil_Template import Template
from openerp.osv import osv, fields

class model_export_xml(osv.osv):
    _name = 'rdef.model.export.xml'
    _description = 'Export data xml of some model'

    _columns = {
        'name':fields.char("File name", size=64 , required=True),
        'model_ids': fields.many2many('ir.model',
                                       'model_xml_generator_rel',
                                       'model_id', 'wizard_id', 'Models',
                                       required=True,
                                       ),
        'xml_file':fields.binary("XML File"),
        'state': fields.selection([('choose', 'choose'),   
                                       ('get', 'get')])
     }
    
    _defaults = { 
        'state': 'choose'
        }
    def export_models(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids, context=context)[0]
        for model_id in this.model_ids:
            ir_model = self.pool.get('ir.model').read(cr, uid, model_id.id, context=context)
            pool_model = self.pool.get(ir_model['model'])
            model_ids = pool_model.search(cr,uid,[],context=context)
            for record_model in pool_model.browse(cr,uid,model_ids):
                print record_model
                
                
        this.write({ 'state': 'get'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rdef.model.export.xml',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
        
model_export_xml()    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
