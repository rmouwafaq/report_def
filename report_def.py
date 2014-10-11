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
import netsvc
import datetime
from tools.translate import _

class ir_module(osv.osv):
    _inherit = "ir.module.module"
    _columns = { 
                'report_def_ids':fields.one2many('report.def','module_id','Reports Definition'),
                }
ir_module()
    
    
class report_def(osv.osv):
    _name = "report.def"
    _description = "Agilorg report Definition"
    _columns = { 
                'name': fields.char('Report Name', size=64, required=True, select=True),
                'title': fields.char('Title', size=128, required=True, select=True),
                'module_id':fields.many2one('ir.module.module', 'Module', required=True),
                'query' : fields.text('Query'),
                'format':fields.selection([('Portrait', 'Portrait'),
                                           ('Landscape','Landscape')],
                                           'Format'),
                    
                'template_html':fields.text('HTML script'),  
                'template_file_name': fields.char('Template File Name', size=128, required=True, select=True),
                'json_file_name': fields.char('JSON File Name', size=128, required=True, select=True),
                'field_ids':fields.one2many('report.def.field','report_id','Report Fields'),
                'total_ids':fields.one2many('report.def.field.total','report_id','Report Totals'),
                'section_bloc_ids':fields.one2many('report.section.bloc','report_id','Sections'),
                } 
#    def hello_func(self, cr, uid,html_content,context=None):
#        pisa.showLogging() 
#        filename = os.getcwd() + "/openerp/addons/report_def_store/static/pdf/testo.pdf"
#        pdf = pisa.CreatePDF(html_content,file(filename, "wb+"))
        
            
            
#        return "ok"
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
        'group':fields.boolean("Groupe"),     
        
        
    }    
    
    _defaults = {'field_type': 'String',
                 'source_data': 'Model',
                 'section' : 'Details'
                 
                 }
                 
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
report_def_field_total()
class report_def_json_files(osv.osv):
    _name = "report.def.json_files"
    _description="Agilorg - Report definition files name json"
    _columns ={
               'name':fields.char('Json Name',size=100,required=True),
               'report_id':fields.many2one('report.def','Report Definition'),
               }
    
report_def_json_files()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: