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
from openerp.osv import osv, fields

class module_templates(osv.osv):
    _name="rdef.module.templates"
    _description ='files data of some dir in some module'

    _columns = {
        'file_name' : fields.char("File Name", size=32),
        'file_size' : fields.char("File Size", size=32),
        'last_update':fields.datetime("Last update")
     }
    
    def create_list_file(self,cr,uid,path_dir,context=None):
        self_ids= self.search(cr,uid,[],context=context)
        self.unlink(cr,uid, self_ids, context=context)
        files_ids=[]
        for file in os.listdir(path_dir):
            vals={
                  'file_name':file,
                  'file_size': str(os.path.getsize(path_dir+file)) +  " octets",
                  'last_update':time.ctime(os.path.getmtime(path_dir+file))
                  }
            id=self.create(cr,uid,vals,context=context)
            files_ids.append(id)
        return files_ids

class template_definition(osv.osv_memory):
    _name = 'rdef.template.definition'
    _description = 'wizard to define report using template'

    _columns = {
        'module_id':fields.many2one('ir.module.module', 'Module',required=True),
        'file_ids': fields.many2many('rdef.module.templates', 
                                       'temp_def_modul_temps_rel',
                                       'template_def_id', 'wizard_id', 'Files',required=True,
                                       ),
        
               
     }
    
    
    def to_define(self, cr, uid, ids, context=None):
        report_def_pool = self.pool.get("report.def")
        this  = self.read(cr,uid,ids,context=context)[0]
        files_ids = this['file_ids']
        files = self.pool.get("rdef.module.templates").read(cr,uid,files_ids,context=context)
        info_template = {}
        for file in files:
            info_template['file_name'] = file['file_name']
            info_template['path_template'] = self.templates_dir
            info_template['module_id'] = this['module_id'][0]
            report_def_pool.create_from_template(cr,uid,info_template,context=context)
        return True
    
    

    def on_change_module(self,cr,uid,ids,module_id,context=None):
        try:
            module_obj=self.pool.get("ir.module.module").read(cr,uid,module_id,context=context)
            self.templates_dir = ao_register.CD_ODOO_ADDONS + module_obj['name'] + '/templates/'
            files_ids=self.pool.get("rdef.module.templates").create_list_file(cr,uid,self.templates_dir,context=context)
            return {'value': {
                'file_ids': [],
                }
            }
        except:
            return False   
    
                
        
                  
template_definition()    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
