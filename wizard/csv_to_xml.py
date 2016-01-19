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
import logging
import openerp
from openerp.osv import osv, fields
from openerp.addons.ao_basic_module.ao_register import CD_ODOO_ADDONS
from openerp.addons.ao_basic_module.ao_class import model_key

from openerp.addons.ao_basic_module.ao_global import create_folder,end_file
from openerp.tools.osutil import listdir
import openerp.tools as tools
import csv
import base64
from StringIO import StringIO

from lxml import etree

_logger = logging.getLogger(__name__)



class csv_to_xml(osv.osv_memory):
   
    _name = 'rdef.csv2xml'
    _description = 'Assistant Convertion csv > xml'

    _columns = {
                'model_id':fields.many2one('ir.model', 'Odoo Model',required=True),
                'data': fields.binary('Fichier CSV à convertir ', required=True),
                
                'name':fields.char("File name", size=64 , required=True),
                'xml_file':fields.binary("XML File"),
                'state': fields.selection([('choose', 'choose'),   
                                           ('get', 'get')]),
     }
    
    _defaults = { 
                 'state': 'choose'
                 }


    def csv_convert_xml(self, cr, uid, ids, context=None):
      
        if context is None:
            context = {}
        
        this = self.browse(cr, uid, ids, context=context)[0]
        xml_file_name = end_file(this.name,'.xml')
        
        data_file = str(base64.decodestring(this['data']))
        my_csv = xml_from_csv(data_file,this.model_id.model)
        print my_csv.convert()
        
        # Save file binary
        encoded_string = base64.b64encode(my_csv.xml) 
        set_data={
                  'xml_file':encoded_string,
                  'name':xml_file_name,
                  'state':'get'
                  }  
        this.write(set_data)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rdef.csv2xml',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
        
csv_to_xml()    


class xml_from_csv(object):
    
    def __init__(self,data_file,my_model):
        # to detect delimiter on the fly
        self.my_model = my_model        
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(data_file, delimiters=',;')
        reader = csv.reader(StringIO(data_file), dialect=dialect)
        self.items = {}
        self.row_model= {}
        self.col_fields = reader.next() 
        self.header = []
        self.def_col = {}
        self.xml  = ''
        self.col_max = len(self.col_fields)
        numcol = 0 
        for col in self.col_fields:
            is_field = False
            is_id = False
            is_ref = False
            key_prefix = ''
            lst_def_field =  col.split('-')
            nb_parm = len(lst_def_field)
            
            for myfield in lst_def_field:
                if myfield == 'id':is_id = True
                if myfield == 'field':is_field = True
                if myfield == 'ref':is_ref = True
                    
            self.header.append(lst_def_field[0])
            
            self.def_col[numcol] = {'name':lst_def_field[0],
                                    'is_id':is_id,
                                    'is_ref':is_ref,
                                    'is_field': is_field,
                                    'key_prefix':key_prefix
                                    }
            self.row_model[numcol] = ''
            numcol +=1

        row_number = 0
        for row in reader:
            numcol= 0
            while (numcol<self.col_max):  
                value = row[numcol].strip()
                if self.items.has_key(row_number):
                    row_value = self.items[row_number]
                else:
                    row_value = self.row_model.copy()
                
                row_value[numcol] = value
                self.items[row_number] = row_value
                numcol +=1 
            row_number +=1

    def convert(self,path_file_name=None):
        
        self.xml = self.xml_header(self.xml )
        self.path_file_name = path_file_name
        row_number = 0 
        for row_number in self.items.keys():
            key_value = self.xml_get_key(row_number)
            self.xml += '        <record id="'+ key_value + '" model="' + self.my_model + '">' + '\n'

            numcol= 0
            while (numcol<self.col_max):
                self.xml = self.xml_set_record(self.xml, row_number, numcol)
                numcol +=1 
            self.xml = self.xml_end_record(self.xml)
                  
        self.xml = self.xml_footer(self.xml)
        
        return self.xml
    
    def xml_header(self,std_temp = ''):
        std_temp += '<?xml version="1.0" encoding="UTF-8"?>' + '\n' 
        std_temp += '<openerp>' + '\n'
        std_temp += '    <data noupdate="0">' + '\n'
        return std_temp 
    
    def xml_get_key(self,row_number):
        
        key_value = ''
        numcol= 0
        row_value = self.items[row_number] 
        while (numcol<self.col_max):
            if self.def_col[numcol]['is_id']:
                if len(key_value)>0:
                    key_value += '_' + row_value[numcol]
                else:
                    key_value = row_value[numcol]     
            numcol +=1 
        return key_value
    
    def xml_set_record(self,std_temp,row_number,numcol):
        
        field_value = self.items[row_number][numcol]
        field_name  = self.def_col[numcol]['name']
        key_prefix  = self.def_col[numcol]['key_prefix']
        is_field    = self.def_col[numcol]['is_field']
        is_ref      = self.def_col[numcol]['is_ref']
        is_id = self.def_col[numcol]['is_id']
        
        if len(key_prefix)>0:
            ref_value   = key_prefix + '_' + field_value
        else:
            ref_value   = field_value  
        
        
        if is_field or is_ref or is_id:
            if is_field or is_id:
                desc_field = '          <field name="' + field_name + '">' + field_value + '</field>'
            if is_ref:
                desc_field = '          <field ref="' + ref_value + '" name="' + field_name + '" />'
            
            std_temp += desc_field + '\n' 
        return std_temp
         
    def xml_end_record(self,std_temp):
        std_temp += '        </record>'+ '\n' 
        return std_temp
    
    def xml_footer(self,std_temp):
        std_temp += '    </data>' +'\n'
        std_temp += '</openerp>' +'\n'
        return std_temp 
    
    def xml_to_file(self,filename,modulename):
        path_folder = CD_ODOO_ADDONS + modulename+"/Report_def/"
        if create_folder(path_folder):
            pass
        
        path_file_name = path_folder+filename
        ofi = open(path_file_name, 'w')
        ofi.write(self.xml)
        ofi.close

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
