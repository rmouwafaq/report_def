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
from openerp.addons.ao_basic_module.ao_register import CD_ODOO_ADDONS

class report_to_xml(osv.osv_memory):
    _name = 'rdef.export.wizard'
    _description = 'Assistant Export Report Definition'

    _columns = {
        'module_id':fields.many2one('ir.module.module', 'Module',required=True),
        'report_ids': fields.many2many('report.def', 
                                       'report_xml_generator_rel',
                                       'report_id', 'wizard_id', 'Reports',
                                       domain="[('module_id','=',module_id)]",required=True,
                                       ),
               
     }
    _defaults = {
      
    }
    
    

    def xml_export_report(self, cr, uid, ids, context=None):
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
            
        values =  self.read(cr, uid, ids, context=context)[0]
        report_ids = values['report_ids']
        print 'values',values
        print 'report_ids',report_ids
        pool_rep = self.pool.get('report.def')
        
        for report_id in report_ids: 
            report = pool_rep.browse(cr,uid, report_id) 
            print 'Nom du rapport ',report.name
            my_xml = xml_gen_model(self.pool,cr,uid,report.xml_file_name)
            my_xml.add_model('report.def','report')
            print my_xml.xml_gen_basic('report.def',report)
         
report_to_xml()    


class xml_gen_model(object):
    
    def __init__(self,pool,cr,uid,path_file_name=None):
        self.pool = pool
        self.cr = cr
        self.uid = uid 
        self.col_model = {}
        self.xml  = ''
        self.xml = self.xml_header(self.xml )
        self.path_file_name = path_file_name
        
         
    def add_model(self,model,obj_name):
        my_model = {'model':model,
                    'name' :obj_name,
                    'value' : None,
                    'desc'  : None,
                    } 
        my_model['desc'] = self.pool.get(model).fields_get(self.cr, self.uid)
        self.col_model[model] = my_model
    
    def xml_gen_basic(self,model,obj_value):
        self.xml += self.xml_generate(model,obj_value)
        # generate childs models
        self.scan_field_one2many(model)
        self.xml_terminate()
        
        module_name=obj_value.module_id.shortdesc
        self.xml_to_file(self.path_file_name,module_name)
        
        return self.xml 
    
    def xml_generate(self,model,obj_value):
        # generate basic model
        self.col_model[model]['value'] = obj_value
        std_temp = ''
        std_temp = self.standard_template(model,std_temp)
        std_temp = self.xml_end_record(std_temp)
        return self.xml_model_template(model,std_temp)
    
    def xml_terminate(self):
        self.xml = self.xml_footer(self.xml)
        
    def get_model(self,model):
        if self.col_model.has_key(model):
            return self.col_model[model]
    
    def standard_template(self,model,std_temp):
        my_model = self.get_model(model)
        model_name = my_model['name'] 
        std_temp += '        <record id="'+'@'+ model_name + '.name'+ '" model="' + my_model['model'] + '">' + '\n' 
        for field_name,value in my_model['desc'].iteritems():
            if value['type'] not in ['one2many','many2one','many2many']:
               std_temp = std_temp  + '            <field name="' + field_name + '">'+'@'+ model_name + '.'+field_name + '</field>' + '\n' 
            
            if value['type'] == 'many2one':
               rel_model = value['relation'] 
               std_temp = std_temp  + '            <field name="'+field_name+ '" ref="@'+rel_model+'@"/>'+ '\n' 
    
        return std_temp
    
        
    def xml_model_template(self,model,str_temp):
        my_model = self.get_model(model)
        model_name = my_model['name'] 
        for field_name,value in my_model['desc'].iteritems():
            if value['type'] not in ['one2many','many2one','many2many']:
                field_value = getattr(my_model['value'], field_name)
                str_value = str(field_value)
                if len(str_value)> 250: 
                    str_value = ''
                str_search = '@'+model_name +'.' + str(field_name)
                str_temp = str_temp.replace(str_search, str_value)
                    
                    
            if value['type'] == 'many2one':
                rel_model = value['relation'] 
                field_value = getattr(my_model['value'], field_name)
                if field_value:
                    str_value = rel_model + '_' + str(getattr(field_value, 'id'))
                    str_temp = str_temp.replace('@'+rel_model+'@', str_value)
                    #str_temp = str_temp.replace('@'+self.obj_name, self.obj_name)
                else:
                    str_temp = str_temp.replace('@'+rel_model+'@', '')
                    
        return str_temp
    
    def xml_header(self,std_temp = ''):
        std_temp += '<?xml version="1.0" encoding="UTF-8"?>' + '\n' 
        std_temp += '<openerp>' + '\n'
        std_temp += '    <data noupdate="0">' + '\n'
        return std_temp 
    
    def xml_end_record(self,std_temp):
        std_temp += '        </record>'+ '\n' 
        return std_temp
    
    def xml_footer(self,std_temp):
        std_temp += '    </data>' +'\n'
        std_temp += '</openerp>' +'\n'
        return std_temp 
    
    def scan_field_one2many(self,model):
        my_model = self.get_model(model)
        model_name = my_model['name'] 
        obj_value = my_model['value'] 
        
        for field_name,value in my_model['desc'].iteritems():
            if value['type'] == 'one2many':
                rel_model = value['relation']
                obj_field = getattr(obj_value, field_name)
                print 'relation model',field_name,rel_model,obj_field
                
                self.add_model(rel_model,'field_name')
                for elet in obj_field:
                    self.xml += self.xml_generate(rel_model,elet)
    
    def xml_to_file(self,filename,modulename):
        path_folder=CD_ODOO_ADDONS+modulename+"/Report_def/"
        if self.create_folder(path_folder):
            pass
        
        path_file_name=path_folder+filename
        print "path_file_name=",path_file_name
        ofi = open(path_file_name, 'w')
        ofi.write(self.xml)
        ofi.close
        
    def create_folder(self, path_target):
        try:
            os.mkdir(path_target)
            return True
        except OSError:
            pass
            return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
