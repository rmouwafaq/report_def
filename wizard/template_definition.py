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
from openerp.addons.ao_basic_module import ao_register
from Agil_Template import Template
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
        report_def_obj = self.pool.get("report.def")
        self_obj = self.read(cr,uid,ids,context=context)[0]
        files_ids = self_obj['file_ids']
        module_id = self_obj['module_id'] 
        files = self.pool.get("rdef.module.templates").read(cr,uid,files_ids,context=context)
        for file in files:
            temp = Template()
            temp.read(self.templates_dir + file['file_name'])
            def_report = temp.get_definition_report()
            if(def_report['name']):
                report_id = report_def_obj.search(cr,uid,[('name','=',def_report['name'])],context=context)
                vals={
                          'name':def_report['name'],
                          'title':def_report['title'] or def_report['name'],
                          'format': def_report['format'][0].upper() + def_report['format'][1:],
                          'module_id':module_id[0],
                          'template_file_name':file['file_name'].split('.')[0],
                          'json_file_name':file['file_name'].split('.')[0] + ".json"
                          }
                
                if(report_id):
                    #set report definition 
                    report_def_obj.write(cr,uid,report_id,vals,context=context)
                    self.write_report_def(cr,uid,temp,report_id[0],context=context)
                else:
                    #add new report definition
                    id_rep_def=report_def_obj.create(cr,uid,vals,context=context)
                    self.create_report_def(cr,uid,temp,id_rep_def,context=context)
                    
        return True
    
    def on_change_module(self,cr,uid,ids,module_id,context=None):
        try:
            module_obj=self.pool.get("ir.module.module").read(cr,uid,module_id,context=context)
            self.templates_dir = ao_register.CD_ODOO_ADDONS + module_obj['name'] + '/templates/'
            files_ids=self.pool.get("rdef.module.templates").create_list_file(cr,uid,self.templates_dir,context=context)
            return True
        except:
            return False   
    
    def write_report_def(self,cr,uid,temp,id_rep_def,context):
        template_def=self.get_data_template(temp)
        sequence_field=0
        
        for sect_key,sect_val in template_def.iteritems():
            section=self.pool.get('report.section.bloc')
            val_section={}
            val_section['report_id']=id_rep_def
            val_section['section']=sect_key
            val_section['max_bloc_number']=sect_val['max_bloc']
            section_id=section.search(cr,uid,[('section','=',sect_key),('report_id','=',id_rep_def)])
            if(section_id):
                section.write(cr,uid,section_id,val_section,context)
                for field_key,field_val in sect_val['fields'].iteritems():  
                    sequence_field+=1      
                    field=self.pool.get('report.def.field')
                    val_field={}
                    val_field['report_id']=id_rep_def
                    val_field['template_id']=field_key
                    val_field['name']=field_key
                    val_field['sequence']=sequence_field
                    val_field['section']=sect_key
                    val_field['source_data']=field_val['source_data']
                    val_field['field_type']=field_val['type']
                    field_id=section.search(cr,uid,[('name','=',sect_key),('report_id','=',id_rep_def)])
                    if(field_id):
                        field.write(cr,uid,field_id,val_field,context)
        return True
    
    def create_report_def(self,cr,uid,temp,id_rep_def,context):
        template_def=self.get_data_template(temp)
        
        sequence_field=0
        
        for sect_key,sect_val in template_def.iteritems():
            section=self.pool.get('report.section.bloc')
            val_section={}
            val_section['report_id']=id_rep_def
            val_section['section']=sect_key
            val_section['max_bloc_number']=sect_val['max_bloc']
            
            section.create(cr,uid,val_section,context)
            for field_key,field_val in sect_val['fields'].iteritems():  
                sequence_field+=1      
                field=self.pool.get('report.def.field')
                val_field={}
                val_field['report_id']=id_rep_def
                val_field['template_id']=field_key
                val_field['name']=field_key
                val_field['sequence']=sequence_field
                val_field['section']=sect_key
                val_field['source_data']=field_val['source_data']
                val_field['field_type']=field_val['type']
                
                field.create(cr,uid,val_field,context)
                
    def get_data_template(self,temp):
        
        sections=['Report_header','Page_header','Details','Page_footer','Report_footer']
        template_def={}
        
        for section_name in sections:
            template_def[section_name]={'max_bloc':temp.get_max_bloc_section(section_name),'fields':{}}
            
            section=temp.get_section(section_name)
            if(section.find(attrs={'class':'Bloc1'})):
                bloc=section.find(attrs={'class':'Bloc1'})
                template_def[section_name]['fields']=dict(temp.get_ids_bloc(bloc))
        return template_def
        
                  
template_definition()    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
