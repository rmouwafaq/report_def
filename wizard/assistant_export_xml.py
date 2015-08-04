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
import logging
import openerp
from openerp.osv import osv, fields
from openerp.addons.ao_basic_module.ao_register import CD_ODOO_ADDONS
from openerp.addons.ao_basic_module.ao_class import model_key

from openerp.addons.ao_basic_module.ao_global import create_folder,end_file
from openerp.tools.osutil import listdir
import openerp.tools as tools


from lxml import etree

_logger = logging.getLogger(__name__)


class odoo_xml(object):
    
    def __init__(self,xmlfile):
        self.xml_doc = self.load_xml_doc(xmlfile)
    
    def get_xml_all_models(self):
        record_tags = {'record': self._get_models}
        self.models = ['ir.module.module']
        if self.xml_doc:
            self.parse(self.xml_doc.getroot(),record_tags)
        return self.models
            
    def _get_models(self,rec,data_node=None):
        rec_model = rec.get("model").encode('ascii')
        self.models.append(rec_model) 
         
    def parse(self, de,tags):
        if not de.tag in ['terp', 'openerp']:
            _logger.error("Mismatch xml format")
            raise Exception( "Mismatch xml format: only terp or openerp as root tag" )

        if de.tag == 'terp':
            _logger.warning("The tag <terp/> is deprecated, use <openerp/>")

        for n in de.findall('./data'):
            for rec in n:
                if rec.tag in tags:
                    try:
                        tags[rec.tag](rec, n)
                    except:
                        _logger.error('Parse error in %s:%d: \n%s',
                                      rec.getroottree().docinfo.URL,
                                      rec.sourceline,
                                      etree.tostring(rec).strip(), exc_info=True)
                        raise
        return True

    def load_xml_doc(self,xmlfile):
        doc = etree.parse(xmlfile)
        root_path = os.path.abspath(os.path.expanduser(os.path.expandvars(os.path.dirname(openerp.__file__))))
        relaxng = etree.RelaxNG(
            etree.parse(os.path.join(root_path,'import_xml.rng' )))
        try:
            relaxng.assert_(doc)
        except Exception:
            _logger.error('The XML file does not fit the required schema !')
            raise
        return doc
    

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
        pool_rep = self.pool.get('report.def')
        
        for report_id in report_ids: 
            report = pool_rep.browse(cr,uid, report_id) 
            if report.xml_file_name:
                xml_file_name = end_file(report.xml_file_name,'.xml')
                my_xml = xml_gen_model(self.pool,cr,uid,xml_file_name)
                my_xml.add_model('report.def','report')
                my_xml.xml_gen_basic('report.def',report)
            else:
                print "nom de fichier xml invalide ",report.xml_file_name
             
report_to_xml()    


class xml_to_report(osv.osv_memory):
    _name = 'rdef.import.wizard'
    _description = 'Assistant Import Report Definition'

    _columns = {
        'module_id':fields.many2one('ir.module.module', 'Module',required=True),
               
     }
    _defaults = {
      
    }

    def xml_import_report(self, cr, uid, ids, context=None):
        """
         To get the module and extract the xml report definition 
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return : retrun report
        """
        if context is None:
            context = {}
        list_report = []    
        values =  self.read(cr, uid, ids, context=context)[0]
        module_id = values['module_id'][0]
        if module_id:
            module = self.pool.get('ir.module.module').browse(cr,uid, module_id)
            pathname = CD_ODOO_ADDONS + module.name + "/Report_def/"
            list_report = listdir(pathname)
       
            for filename in list_report:
                open_file = pathname + filename
                fp = tools.file_open(open_file)
                obj_xml_odoo =  odoo_xml(fp)
                my_models = obj_xml_odoo.get_xml_all_models()
                pool_ir_data = self.pool.get('ir.model.data')
                for rec_model in my_models:
                    pool_ir_data.export_external_ids(cr,uid,rec_model,module_id)
                fp.close()
            
            for filename in list_report:
                open_file = pathname + filename
                fp = tools.file_open(open_file)
                try:
                    tools.convert_xml_import(cr, module.name,
                                             fp, 
                                             None, 
                                             'init', 
                                             True, 
                                             None)
                finally:
                    fp.close()
                    
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
        
        module_name = obj_value.module_id.name
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
        
    def get_key_name(self,model_name):
        pool_model = self.pool.get(model_name)
        desc  = pool_model.fields_get(self.cr, self.uid)
        def_model = dir(pool_model)
        if ('_key_name' in def_model):
            key_name = model_key(pool_model._key_name,desc)
            return key_name 
        return "id"
    
    def standard_template(self,model,std_temp):
        
        my_model   = self.get_model(model)
        key_name   = self.get_key_name(model)
        model_name = my_model['name']

        key_value = key_name.val_to_string(my_model['value'])
        std_temp += '        <record id="'+ key_value + '" model="' + my_model['model'] + '">' + '\n' 
        for field_name,value in my_model['desc'].iteritems():
            if value['type'] not in ['one2many','many2one','many2many']:
               field_value = getattr(my_model['value'], field_name)
               if field_value :
                   std_temp = std_temp  + '            <field name="' + field_name + '">'+'@'+ model_name + '.'+field_name + '</field>' + '\n'
                   #std_temp = std_temp  + '            <field name="' + field_name + '">'+str(field_value) + '</field>' + '\n'
            if value['type'] == 'many2one':
               relation_model = value['relation'] 
               rel_model = relation_model.replace('.','_')
               field_value = getattr(my_model['value'], field_name)
               if(field_value):
                   str_value = self.relation_set_value(relation_model,field_value)
                   std_temp = std_temp  + '            <field name="'+field_name+ '" ref="'+str_value+'"/>'+ '\n' 
     
        return std_temp

    def relation_set_value(self,relation_model,field_value):
        key_name = self.get_key_name(relation_model)
        value = getattr(field_value, 'id')
        if not key_name._key == 'id':
            value = self.search_relation_value(relation_model,key_name,value)
        return str(value)
        
            
    def relation_many2one(self,my_model,field_name,value,str_temp):
        relation_model = value['relation'] 
        rel_model = relation_model.replace('.','_')
        field_value = getattr(my_model['value'], field_name)
        if field_value:
            str_value = self.relation_set_value(relation_model,field_value)
            str_temp = str_temp.replace('@'+rel_model+'@', str_value)
        else:
            str_temp = str_temp.replace('@'+rel_model+'@', '')
        return str_temp
        
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
                str_temp = self.relation_many2one(my_model,field_name,value,str_temp)
                    
        return str_temp
       
    def search_relation_value(self,model,key_name,id):
        ids = self.pool.get(model).search(self.cr,self.uid,[('id','=',id)])
        res = self.pool.get(model).read(self.cr,self.uid,ids)
        return key_name.val_to_string(res[0])
     
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
                
                if(obj_value!=None):
                    obj_field = getattr(obj_value, field_name)
                    self.add_model(rel_model,'field_name')
                    for elet in obj_field:
                        self.xml += self.xml_generate(rel_model,elet)
                    self.scan_field_one2many(rel_model)
                    
    
    def xml_to_file(self,filename,modulename):
        path_folder = CD_ODOO_ADDONS + modulename+"/Report_def/"
        if create_folder(path_folder):
            pass
        
        path_file_name = path_folder+filename
        ofi = open(path_file_name, 'w')
        ofi.write(self.xml)
        ofi.close
    
        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
