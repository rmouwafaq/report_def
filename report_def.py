
from openerp.osv import fields, osv
import ho.pisa as pisa
import os
import time
import netsvc
import datetime
from tools.translate import _

    
    
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
import time
import netsvc
import datetime
from tools.translate import _

class ir_module(osv.osv):
    _inherit = "ir.module.module"
    _columns = { 
                'report_def_ids':fields.one2many('report.def','module_id','Reports Definition'),
                }
ir_module()

class res_company(osv.osv):  
    _inherit="res.company" 
    
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
    _columns = { 
                'name': fields.char('Report Name', size=64, required=True, select=True),
                'title': fields.char('Title', size=128, required=True, select=True),
                'module_id':fields.many2one('ir.module.module', 'Module',required=True),
                'query' : fields.text('Query'),
                'format':fields.selection([('Portrait', 'Portrait'),
                                           ('Landscape','Landscape')],
                                           'Format'),
                'type':fields.selection([('normal', 'Normal'),
                                           ('form','Formulary')],
                                           'Type'),  
                'template_html':fields.text('HTML script'),  
                'template_file_name': fields.char('Template File Name', size=128, required=True, select=True),
                'json_file_name': fields.char('JSON File Name', size=128, required=True, select=True),
                'field_ids':fields.one2many('report.def.field','report_id','Report Fields'),
                'total_ids':fields.one2many('report.def.field.total','report_id','Report Totals'),
                'section_bloc_ids':fields.one2many('report.section.bloc','report_id','Sections'),
                } 
    
    def to_dict(self,cr,uid,name=None,id=None):
        
        dict_report={}
        if name:
            id = self.search(cr,uid, [('name','=',name)])
        else:
            id = self.search(cr,uid, [('id','=',id)])
        
        if id:
            report = self.browse(cr,uid, id)[0]  
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
            
            dict_report['col_totals']=[]
            for total_id in report.total_ids:
                dict_report['col_totals'].append(total_id.to_dict())
                
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
    _columns = { 
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
    _columns = { 
        'template_id':fields.char('Template html id', size=64, required=True, select=True),        
        'name': fields.char('Field Name', size=64, required=True, select=True),        
        'report_id':fields.many2one('report.def', 'Report Definition'),
        'total_id':fields.many2one('report.def.field.total', 'Total field'),
        
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
                                        ('Date','Date'),
                                        ('Datetime','Datetime'),
                                        ('Time','Time'),
                                        ('Image','Image'),
                                        ('Static Image','Static Image'),
                                        ],'Field Type'),
        'expression':fields.text('Expression'),
        'group':fields.boolean("Grouped")        
        
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
            if report_def_field.total_id :
                dict_report_def_field['total_id']=report_def_field.total_id.id
            else:
                dict_report_def_field['total_id']=0
            dict_report_def_field['sequence']=report_def_field.sequence
            dict_report_def_field['section']=report_def_field.section
            dict_report_def_field['source_data']=report_def_field.source_data
            dict_report_def_field['field_type']=report_def_field.field_type
            dict_report_def_field['expression']=report_def_field.expression
            
            return dict_report_def_field
        else:
            return dict_report_def_field   
                 
report_def_field()


class report_def_field_total(osv.osv):
    _name = "report.def.field.total"
    _description = "Agilorg - Report Definition field Total"
    _columns = { 
                'name': fields.char('Total Name', size=64, required=True, select=True),
                'report_id':fields.many2one('report.def', 'Report Definition'),
                'function':fields.selection([ ('Sum', 'Sum'),
                                                    ('Average','Average'),
                                                    ('Count','Count'),
                                                  ],'Total function'),
                'reset_after_print':fields.boolean('Reset after print'),
                'reset_repeat_section':fields.boolean('Reset for repeated section'),
                'field_ids':fields.one2many('report.def.field','total_id','Total Fields'),
    }    
    
    
    def to_dict(self,cr,uid,id=None):
        
        dict_report_def_field_total={}
        
        id = self.search(cr,uid, [('id','=',id)])
        
        if id:
            report_def_field_total = self.browse(cr,uid, id)[0]  
            dict_report_def_field_total['id']=report_def_field_total.id
            dict_report_def_field_total['name']=report_def_field_total.name
            dict_report_def_field_total['report_id']=report_def_field_total.report_id.id
            dict_report_def_field_total['function']=report_def_field_total.function
            dict_report_def_field_total['reset_after_print']=report_def_field_total.reset_after_print
            dict_report_def_field_total['reset_repeat_section']=report_def_field_total.reset_repeat_section
            
            dict_report_def_field_total['col_fields']=report_def_field_total.field_ids
            
            return dict_report_def_field_total
        else:
            return dict_report_def_field_total 
          
report_def_field_total()


class report_def_json_files(osv.osv):

    _name = "report.def.json_files"
    _description="Agilorg - Report definition files name json"
    _columns ={
               'name':fields.char('Json Name',size=100,required=True),
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
            #dict_report['col_fields']=
            #dict_report['col_totals']=
            #dict_report['section_bloc_ids']=
            
            return dict_report
        else:
            return dict_report   
    
report_def_json_files()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: