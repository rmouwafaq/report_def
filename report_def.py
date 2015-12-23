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
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from agilreport.Agil_Template import Template
from mock import self
from openerp.addons.ao_basic_module import ao_register
from openerp.addons.ao_basic_module.ao_class import model_key
from openerp.addons.ao_basic_module.ao_global import end_file

import os
import datetime
import base64
from openerp.addons.ao_basic_module.ao_register import CD_AO_FIN_REPORT,CD_REPORT_DEF

RDEF_FORMAT_SELECTION = [('Portrait', 'Portrait'),
                         ('Landscape','Landscape')]

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
            if type(key_name) is model_key:
                key_value =  key_name.val_to_string(record)
            else :
                key_value=str(record[key_name])
                
            values = {  'name': key_value,
                        'model': rec_model,
                        'module': module.name,
                        'res_id': record['id'],
                        'noupdate': False
                        }
            ir_id = pool_ir_data.search(cr, uid, [('name','=',key_value),('module','=',module.name)])
            if not ir_id:
                ir_id = pool_ir_data.create(cr,uid,values,context=None)
                
             
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
                'format':fields.selection(RDEF_FORMAT_SELECTION,'Format'),
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
                'xml_file_name': fields.char('Xml File Name', size=128),
                'viewer_type': fields.selection([('html', 'HTML'),
                                                 ('pdf','PDF')],
                                                'Viewer Type'),
                
                'deferred_total':fields.boolean("Deferred totals"),
                'deferred_label_field': fields.many2one('report.def.field','Label in field'),
                'deferred_label': fields.char('Deferred Label', size=64),
                'reset_total_by_group':fields.boolean("Reset total by group"),  
                }
    
    _defaults = {'deferred_label': 'Report' }
    
    
    def get_path_template_name(self,cr,uid,report_id,template_name,context=None):
        module_rep = self.pool.get("ir.module.module").browse(cr,uid,report_id,context) 
        module_folder_name  = ao_register.CD_ODOO_ADDONS + module_rep.name + '/templates/'
        template_name = end_file(template_name,'.html')
        return module_folder_name + template_name
            
#     def create(self,cr,uid,vals,context=None():
#         id_rep_def = super(report_def,self).create(cr, uid, vals, context)
#         path_template = self.get_path_template_name(cr,uid,vals['module_id'],vals['template_file_name'],context=None)
#         if(vals.get('auto_generate',False)) and path_template:
#             self.auto_create_fields(cr, uid,path_template,id_rep_def,context)
#         return id_rep_def

    
    def create_dynamic_report(self,cr,uid,report_name,context):

        report_def_ids = self.search(cr,uid,[('name','=',report_name)],context=context)
        report_def_id = None
        if(report_def_ids):
            report_def_id = report_def_ids[0]
        else:
            info_template = {
                  'name':report_name,
                  'title':context.get('title',report_name),
                  'module_id':context.get('module_id',0),
                  'template_file_name':end_file(report_name,'.html'),
                  'json_file_name':end_file(report_name,".json"),
                  'format':context.get('type_doc','Landscape'),
                  'type':context.get('type_doc','form'),
                  'viewer_type':context.get('viewer_type','html'),
                  }
            report_def_id = self.create(cr,uid,info_template,context=context)
        return report_def_id
    
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
    
    def create_from_template(self,cr,uid,info_template,context=None):
        
        temp = Template()
        temp.read(info_template['path_template'] + info_template['template_file_name'])
        
        #if not info_template.has_key('name'):
        info_template = temp.get_definition_report(info_template)
        if(info_template.has_key('name')):
            report_id = self.search(cr,uid,[('name','=',info_template['name'])],context=context)
            vals={    'name':info_template['name'],
                      'title':info_template['title'] or info_template['name'],
                      'format': info_template['format'],
                      'module_id':info_template['module_id'],
                      'template_file_name':end_file(info_template['template_file_name'],'.html'),
                      'json_file_name':end_file(info_template['template_file_name'],'.json'),
                      'type':info_template['type'],
                      'viewer_type':info_template['viewer_type'],
                      }
            
            if(report_id):
                #set report definition 
                self.write(cr,uid,report_id,vals,context=context)
                self.write_report_def(cr,uid,temp,report_id[0],context=context)
                return report_id[0]
            else:
                #add new report definition
                report_id = self.create(cr,uid,vals,context=context)
                self.create_report_def(cr,uid,temp,report_id,context=context)
                return report_id
        else:
            raise osv.except_osv('Action Error !',"No report definition in template " + info_template['template_file_name'])
                
    
    def write_report_def(self,cr,uid,temp,id_rep_def,context):
        
        template_def = temp.get_data_template()
        sequence_field = 0
        section = self.pool.get('report.section.bloc')
        field = self.pool.get('report.def.field')
        
        for sect_key,sect_val in template_def.iteritems():
            val_section={}
            val_section['report_id'] = id_rep_def
            val_section['section'] = sect_key
            val_section['max_bloc_number'] = sect_val['max_bloc']
            section_id = section.search(cr,uid,[('section','=',sect_key),('report_id','=',id_rep_def)])
            if(section_id):
                section.write(cr,uid,section_id,val_section,context)
                for field_key,field_val in sect_val['fields'].iteritems():  
                    sequence_field+=1      
                    
                    val_field={}
                    val_field['report_id']=id_rep_def
                    val_field['template_id']=field_key
                    val_field['name']=field_key
                    val_field['sequence']=sequence_field
                    val_field['section']=sect_key
                    val_field['source_data']=field_val['source_data']
                    val_field['field_type']=field_val['type']
                    val_field['formula']=field_val['formula']
                    
                    field_id = section.search(cr,uid,[('name','=',sect_key),('report_id','=',id_rep_def)])
                    if(field_id):
                        field.write(cr,uid,field_id,val_field,context)
        return True
    
    def create_report_def(self,cr,uid,temp,id_rep_def,context):

        template_def = temp.get_data_template()
        print 'template definition ',template_def
        sequence_field = 0
        
        for sect_key,sect_val in template_def.iteritems():
            
            section=self.pool.get('report.section.bloc')
            val_section = {}
            val_section['report_id'] = id_rep_def
            val_section['section'] = sect_key
            val_section['max_bloc_number'] = sect_val['max_bloc']
            
            section.create(cr,uid,val_section,context)
            for field_key,field_val in sect_val['fields'].iteritems():  
                print 'fields',field_key,field_val
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
            dict_report['template_html'] = report.template_html
            dict_report['template_file_name'] = end_file(report.template_file_name,'.html')
            dict_report['json_file_name'] = end_file(report.json_file_name,'.json')
            dict_report['viewer_type'] = report.viewer_type
            
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
        

class report_field_format(osv.osv):
    _name = "report.field.format"
    _description = "DefReport field Format"
    _columns = {
                'name':fields.char('name',size=64), 
                'format':fields.char('format',size=64),
                'function':fields.char('function',size=64),
                }
    
    _defaults = {'format': '{:>5,.2f}' }
    
    def to_dict(self,cr,uid,id=None):
        
        dict_report_format={}
        id = self.search(cr,uid, [('id','=',id)])
        if id:
            report_format = self.browse(cr,uid, id)[0] 
            dict_report_format['id']   = report_format.id
            dict_report_format['name'] = report_format.name
            dict_report_format['format'] = report_format.format
            dict_report_format['function'] = report_format.function
            return dict_report_format
        else:
            return dict_report_format   
        
report_field_format()

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
                                        ('Global','Global'),
                                        ('Page','Current Page'),
                                        ('Folio','Current folio'),
                                        ('Pages','Total Pages'),
                                        ('Folios','Total folios'),
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
        'field_format_id':fields.many2one('report.field.format', 'Field Format'),
        
        'expression':fields.text('Expression'),
        'formula':fields.text('formule'),
        
        'group':fields.boolean("Grouped"),
        'function':fields.selection([ ('Sum', 'Sum'),
                                      ('Average','Average'),
                                      ('Count','Count'),
                                      ],'Total function'),
         'reset_after_print':fields.boolean('Reset after print'),
         'reset_repeat_section':fields.boolean('Reset for repeated section'),        
         'total_field_id': fields.many2one('report.def.field','Related - Total Field'),
         'related_field_id': fields.many2one('report.def.field','Related Field (2)'),
    
    }    
    
    _defaults = {'field_type': 'String',
                 'source_data': 'Model',
                 'section' : 'Details'
                 
                 }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name + ' - ' + record.field_type + ' - ' + record.source_data  
            res.append((record.id, name))
        return res

                 
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
            dict_report['template_file_name'] = end_file(report.template_file_name,'.html')
             
            return dict_report
        else:
            return dict_report   
    
report_def_json_files()

class report_def_request(osv.osv):

    _name = "report.def.request"
    _description="Agilorg - Report definition request"
    _columns ={
               'report_id':fields.many2one('report.def','Report Definition'),
               'file_request':fields.binary('Request file')
               }
    
    def set_action_request_report(self,cr,uid,report_def_id,bin_report,context=None):
        rep_request_id = self.create(cr,uid,
                                          {'report_id':report_def_id,
                                           'file_request':bin_report
                                           },context=context)
        
        action ={
                'type' : 'ir.actions.client',
                'name' : 'report_def.Report Viewer Action',
                'tag' : 'report.viewer.action',
                'params' : {'id':rep_request_id},
                #'context':context
                } 
       
        return action
    
    def report_viewer(self,cr,uid,ids,context=None):
        return {
                    'type' : 'ir.actions.client',
                    'name' : 'report_def.Report Viewer Action',
                    'tag' : 'report.viewer.action',
                    'params' : {'id':ids[0]},
                    
                }
        
report_def_request()

class report_request_view(osv.osv):
    
    _name = "report.request.view"
    _description = "report request Sqlview"
    _auto        = False
    _columns = {
        'id': fields.integer('report request id', readonly=True),
        'report_id' :fields.integer('report_def id', readonly=True),
        'name': fields.char('name',size=64, readonly=True),
        'viewer_type':fields.char('viewer_type',size=64, readonly=True),
        'file_request':fields.binary('file request', readonly=True),
        'create_uid':fields.integer("create_uid", readonly=True),
        'create_date':fields.datetime("create date", readonly=True),
        'write_uid':fields.integer('write uid', readonly=True),
        'write_date':fields.datetime("write date", readonly=True),
        
        
    }
    

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_request_view')
        cr.execute("""
            create or replace view report_request_view as (
            select 
                rdr.id,
                rdr.report_id,
                rd.name,    
                rd.viewer_type,
                rdr.file_request,
                rdr.create_uid,
                rdr.create_date,
                rdr.write_uid,
                rdr.write_date
            from report_def rd,report_def_request rdr
            where rd.id=rdr.report_id
            )""")
    def report_to_pdf(self,cr,uid,id_report):
        report_request   = self.pool.get("report.def.request")
        current_request_rep = report_request.browse(cr,uid,id_report,context=None)
        
        today = datetime.datetime.now()
        file_name = "tmp_"+str(uid)+"_"+str(today.date())+"_"+str(today.time())
        path_dir = CD_REPORT_DEF+"/static/lib/temp/"
        
        temp=Template()
        file_content=current_request_rep.file_request
        temp.set_content_html(file_content.decode("utf-8"))
        temp.copie(path_dir+file_name+".html")
         
        save_pdf = temp.save_pdf_from_file(path_dir+file_name+".html",path_dir+file_name+".pdf","portrait")
        return path_dir+file_name+".pdf"
        
#         with open(path_dir+"test.pdf", 'r+') as template_file:
#             return template_file 
report_request_view()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
