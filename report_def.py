# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Agilorg (<http://www.agilorg.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#e
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp.osv import fields, osv
import ho.pisa as pisa
import os
import time
import openerp.netsvc
import datetime
from openerp.tools.translate import _
from Agil_Template import Template
from checkbox.lib.transport import create_connection
from mock import self
from asyncore import write
from openerp.addons.ao_basic_module import ao_register
from openerp.addons.ao_basic_module.ao_class import model_key


class ir_module(osv.osv):
    _inherit = "ir.module.module"
    _key_name = 'name'
    _columns = { 
                'report_def_ids':fields.one2many('report.def','module_id','Reports Definition'),
                }
    
ir_module()

class ir_model_data(osv.osv):

    _inherit = "ir.model.data"
    
    def get_key_name(self,cr,uid,model_name):
        pool_model = self.pool.get(model_name)
        desc  = pool_model.fields_get(cr,uid)
        def_model = dir(pool_model)
        if ('_key_name' in def_model):
            key_name = model_key(pool_model._key_name,desc)
            return key_name 
        return "id"
    
        
    def export_external_ids(self,cr,uid,rec_model,module_id):
        module = self.pool.get('ir.module.module').browse(cr,uid,module_id)
        pool_model = self.pool.get('ir.model')
        pool_ir_data = self.pool.get('ir.model.data')
        model_id = pool_model.search(cr, uid, [('model','in',[rec_model])])
        key_name = self.get_key_name(cr,uid,rec_model)
        
        pool_data = self.pool.get(rec_model)
        
        ir_ids = pool_ir_data.search(cr,uid,[('module','in',[module.name]),
                                             ('model','in',[rec_model])])
        pool_ir_data.unlink(cr,uid,ir_ids,context=None)
        
        all_model_ids = pool_data.search(cr, uid, [])
        result        = pool_data.read(cr, uid, all_model_ids)
        for record in result:
            key_value =  key_name.val_to_string(record)
            values = {  'name': key_value,
                        'model': rec_model,
                        'module': module.name,
                        'res_id': record['id'],
                        'noupdate': False
                        }
            ir_id = pool_ir_data.search(cr, uid, [('name','=',key_value),('module','=',module.name)])
            if not ir_id:
                ir_id = pool_ir_data.create(cr,uid,values,context=None)
                
            print 'key_value',rec_model,key_value
             
ir_model_data()


class res_company(osv.osv):  
    
    _inherit = "res.company" 

    def to_dict(self,cr,uid,id=None):
        
        dict_company={}
        id = self.search(cr,uid, [('id','=',id)])
        
        if id:
            company = self.browse(cr,uid, id)[0]  
            dict_company['id']=company.id
            
            dict_company['name']=(company.partner_id).to_dict()
            
            return dict_company
        else:
            return dict_company

class res_users(osv.osv):  
    _inherit="res.users" 
    
    def to_dict(self,cr,uid,id=None):
        
        dict_user={}
        id = self.search(cr,uid, [('id','=',id)])
        
        if id:
            user = self.browse(cr,uid, id)[0]  
            dict_user['id']=user.id
            dict_user['partner']=(user.partner_id).to_dict()
            dict_user['company']=(user.company_id).to_dict()
            
            return dict_user
        else:
            return dict_user

class res_partner(osv.osv):  
    
    _inherit="res.partner" 
    
    def to_dict(self,cr,uid,id=None):
        
        dict_partner={}
        id = self.search(cr,uid, [('id','=',id)])
        
        if id:
            partner = self.browse(cr,uid, id)[0]  
            dict_partner['id']=partner.id
            dict_partner['name']=partner.name
            
            return dict_partner
        else:
            return dict_partner

class report_def(osv.osv):
    
    _name = "report.def"
    _description = "Agilorg report Definition"
    _key_name = 'name'
    _columns = { 
                'name': fields.char('Report Name', size=64, required=True, select=True),
                'title': fields.char('Title', size=128, required=True, select=True),
                'module_id':fields.many2one('ir.module.module', 'Module',required=True),
                'query' : fields.text('Query'),
                'format':fields.selection([('Portrait', 'Portrait'),
                                           ('Landscape','Landscape')],
                                           'Format'),
                'type':fields.selection([('normal', 'Normal'),
                                         ('user', 'User'),
                                         ('form','Formulary')],
                                           'Type'),  
                
                'template_html':fields.text('HTML script'),  
                'template_file_name': fields.char('Template File Name', size=128, required=True),
                'json_file_name': fields.char('JSON File Name', size=128, required=True),
                'field_ids':fields.one2many('report.def.field','report_id','Report Fields'),
                'section_bloc_ids':fields.one2many('report.section.bloc','report_id','Sections'),
                'auto_generate':fields.boolean("Auto generate data"),
                'out_template_file_name':fields.char('Output template file name',size=256),
                'xml_file_name': fields.char('Xml File Name', size=128)
                
                }
    
    def get_path_template_name(self,cr,uid,report_id,template_name,context=None):
        module_rep = self.pool.get("ir.module.module").browse(cr,uid,report_id,context) 
        module_folder_name  = ao_register.CD_ODOO_ADDONS + module_rep.name + '/templates/'
        if not template_name.endswith('.html'):
            template_name = template_name + '.html'
        return module_folder_name + template_name
            
    def create(self,cr,uid,vals,context=None):
        id_rep_def = super(report_def,self).create(cr, uid, vals, context)
        path_template = self.get_path_template_name(cr,uid,vals['module_id'],vals['template_file_name'],context=None)
        print "vals:",vals
        if(vals.get('auto_generate',False)) and path_template:
            self.auto_create_fields(cr, uid,path_template,id_rep_def,context)
        return id_rep_def
    
    def auto_create_fields(self,cr,uid,template_dir,id_rep_def,context):
        sections=['Report_header','Page_header','Details','Page_footer','Report_footer']
        temp=Template()
        temp.read(template_dir)
        template_def={}
        for section_name in sections:
            template_def[section_name]={'max_bloc':temp.get_max_bloc_section(section_name),'fields':{}}
            
            section=temp.get_section(section_name)
            if(section.find(attrs={'class':'Bloc1'})):
                bloc=section.find(attrs={'class':'Bloc1'})
                template_def[section_name]['fields']=dict(temp.get_ids_bloc(bloc))
        
        
        self.write(cr, uid, id_rep_def,{'template_html':temp.content_html}, context)        
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
    
    
    def to_dict(self,cr,uid,name=None,id=None):
        
        dict_report = {}
        if name:
            print 'recherche par Nom',name
            ids = self.search(cr,uid, [('name','=',name)])
        else:
            print 'recherche par id',id
            ids = self.search(cr,uid, [('id','=',id)])
            
        if ids:
            print "Id trouve de defreport",ids
            report = self.browse(cr,uid, ids)[0]  
            dict_report['id']=report.id
            dict_report['name']=report.name
            dict_report['title']=report.title
            dict_report['module_id']=report.module_id.id
            dict_report['query']=report.query
            dict_report['format']=report.format
            dict_report['type']=report.type
            dict_report['template_html']=report.template_html
            dict_report['template_file_name']=report.template_file_name
            dict_report['json_file_name']=report.json_file_name
            
            
            dict_report['col_fields']=[]
            for field_id in report.field_ids:
                dict_report['col_fields'].append(field_id.to_dict())
            
                
            dict_report['col_sections']=[]
            for section_bloc_id in report.section_bloc_ids:
                dict_report['col_sections'].append(section_bloc_id.to_dict())
            
            return dict_report
        else:
            return dict_report         

report_def()
        

class report_section_bloc(osv.osv):
    _name = "report.section.bloc"
    _description = "DefReport section Bloc"
    _key_name = 'section'
    _columns = {
                'name':fields.char('name',size=64), 
                'report_id':fields.many2one('report.def', 'Report Definition'),
                'section' : fields.selection([('Report_header', 'Report_header'),
                                           ('Page_header', 'Page_header'),
                                           ('Details','Details'),
                                           ('Page_footer','Page_footer'),
                                           ('Report_footer','Report_footer'),
                                           ('Images','Images'),
                                            ],'Report Section'), 
                'max_bloc_number':fields.integer('Max Bloc'),
                }
    
    _defaults = {'max_bloc_number': 1 }
    
    def onchange_section(self,cr,uid,ids,selected_section,context=None):
        res={}
        print  selected_section
        res['value']={'name':selected_section}
        return res
    
    def to_dict(self,cr,uid,id=None):
        
        dict_report_section={}
        
        id = self.search(cr,uid, [('id','=',id)])
        
        if id:
            report_section = self.browse(cr,uid, id)[0] 
            dict_report_section['id']=report_section.id
            dict_report_section['report_id']=report_section.report_id.id
            dict_report_section['section']=report_section.section
            dict_report_section['max_bloc_number']=report_section.max_bloc_number
            
            return dict_report_section
        else:
            return dict_report_section   
        
report_section_bloc()


class report_def_field(osv.osv):
    
    _name = "report.def.field"
    _description = "Agilorg Report Definition fields"
    _order =  "sequence,section"
    _key_name = 'name'
    _columns = { 
        'template_id':fields.char('Template html id', size=64, required=True, select=True),        
        'name': fields.char('Field Name', size=64, required=True, select=True),        
        'report_id':fields.many2one('report.def', 'Report Definition'),
       
        'sequence' : fields.integer('Sequence', size=6),
        'section' : fields.selection([('Report_header', 'Report_header'),
                                       ('Page_header', 'Page_header'),
                                       ('Details','Details'),
                                       ('Page_footer','Page_footer'),
                                       ('Report_footer','Report_footer'),
                                       ('Images','Images'),
                                        ],'Report Section'), 

        'source_data':fields.selection([('Model', 'Model'),
                                        ('Form','Form'),
                                        ('Context','Context'),
                                        ('Total','Total'),
                                        ('Computed','Computed'),
                                        ('Function','Function'),
                                        ('Html','Html'),
                                        ],'Source Data'),
                
        'field_type':fields.selection([ ('Number', 'Number'),
                                        ('String','String'),
                                        ('Double','Double'),
                                        ('Integer','Integer'),
                                        ('Currency','Currency'),
                                        ('List','List'),
                                        ('Dict','Dict'),
                                        ('Date','Date'),
                                        ('Datetime','Datetime'),
                                        ('Time','Time'),
                                        ('Image','Image'),
                                        ('Static Image','Static Image'),
                                        ],'Field Type'),
        'expression':fields.text('Expression'),
        'formula':fields.text('formule'),
        
        'group':fields.boolean("Grouped"),
        'function':fields.selection([ ('Sum', 'Sum'),
                                      ('Average','Average'),
                                      ('Count','Count'),
                                      ],'Total function'),
         'reset_after_print':fields.boolean('Reset after print'),
         'reset_repeat_section':fields.boolean('Reset for repeated section'),        
        
    }    
    
    _defaults = {'field_type': 'String',
                 'source_data': 'Model',
                 'section' : 'Details'
                 
                 }
                 
    def to_dict(self,cr,uid,id):
        
        dict_report_def_field={}
        
        id = self.search(cr,uid, [('id','=',id)])
        
        if id:
            report_def_field = self.browse(cr,uid, id)[0]  
            
            dict_report_def_field['id']=report_def_field.id
            dict_report_def_field['template_id']=report_def_field.template_id
            dict_report_def_field['report_id']=report_def_field.report_id.id
            dict_report_def_field['name']=report_def_field.name
            dict_report_def_field['sequence']=report_def_field.sequence
            dict_report_def_field['section']=report_def_field.section
            dict_report_def_field['source_data']=report_def_field.source_data
            dict_report_def_field['field_type']=report_def_field.field_type
            dict_report_def_field['expression']=report_def_field.expression
            
            return dict_report_def_field
        else:
            return dict_report_def_field   
                 
report_def_field()

    
    


class report_def_json_files(osv.osv):

    _name = "report.def.json_files"
    _description="Agilorg - Report definition files name json"
    _key_name = 'name'
    _columns ={
               'name':fields.char('Json Name',size=128,required=True),
               'report_id':fields.many2one('report.def','Report Definition'),
               }

    def to_dict(self,cr,uid,name=None,id=None):
        
        dict_report={}
        if name:
            id = self.search(cr,uid, [('name','=',name)])
        else:
            id = self.search(cr,uid, [('id','=',id)])
        
        if id:
            report = self.browse(cr,uid, id)[0]  
            dict_report['name']=report.name
            dict_report['title']=report.titile
            dict_report['module']=report.module_id.name
            dict_report['query']=report.query
            dict_report['format']=report.format
            dict_report['template_html']=report.template_html
            dict_report['template_file_name']=report.template_file_name
             
            return dict_report
        else:
            return dict_report   
    
report_def_json_files()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
