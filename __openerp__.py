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
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    "name" : "Report Definition",
    "version" : "0.01",
    "author": ["Agilorg ", "OpenERP SA" ],
    "category" : " Report tools",
    "sequence": 0,
    "description": """
     Report Tools.
    """,
    "website": ["http://www.agilorg.com"],
    "depends" : ["base"],
    "init_xml" : [],
    "demo" : [],
    "data" : ["report_viewer.xml",
              "def_report_view.xml",
              "wizard/export_rep_def_view.xml",
              "wizard/template_definition.xml",
              "wizard/model_export_xml_view.xml",
              "menu_action.xml",
              ],
    "js": ["static/lib/engine_report.js","static/src/js/report_viewer_template.js"],
    "css":[],
    "qweb":["static/src/xml/report_viewer_template.xml"],
    "auto_install": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: