import datetime
import time
import json
import collections
import os

class report_api():
    
    def init_class(self,cr,uid,pool,datas,report_name= '',report_def_id = 0): 
        self.cursor = cr 
        self.user_id = uid 
        self.result = {}
        self.report_context = {}
        self.pool=pool
        cid = 1 
        
        
        ref_report = {'model':'report.def',
                      'name':report_name,
                      'id':report_def_id}
        
        data_test=self.pool.get('report.def').browse(cr, uid, 2)
        print "test data browser",data_test
        
        report = self.get_object_model(ref_report)
        self.report_context = self.update_context('report',report)
        
        ref_company = {'model':'res.company',
                      'id':cid}
        
        company = self.get_object_model(ref_company)
        self.report_context = self.update_context('company',company)
        
        ref_user = {'model':'res.users',
                      'id':uid}
        
        user = self.get_object_model(ref_user)
        self.report_context = self.update_context('user',user)
        
        self.report_context = self.update_context('datas',datas)
        
        self.cur_report = current_report(self.report_context)
        
        query = self.cur_report.replace_form_values(self.cur_report.report.query)
        self.cursor.execute(query)
        self.result = self.cursor.dictfetchall() 
        self.max_bloc_details = self.cur_report.get_max_bloc_section('Details')
       
#        list_group = {}
#        print "result :: ",self.result
#        for record in self.result:
#            cur_key_group = cur_report.key_group_value(record)
#            print "cur_key_group",cur_key_group
#            if list_group.has_key(cur_key_group) == True:
#                my_list = list_group[cur_key_group]
#            else: 
#                my_list = []
#                
#            my_list.append(record)
#            list_group[cur_key_group]=my_list
#            
##            print cur_key_group,my_list
#        print "list group :: ",list_group            
#        for key,list_record in list_group.iteritems():
#            self.print_report(cur_report,list_record)
        
#======================================================
        self.total_record_list=0
        self.total_record_all_list=len(self.result)
#======================================================
        list_records=[]
        key_name=""
        if(self.cur_report.field_key_group):
            key_name=self.cur_report.field_key_group[0]
            first_record=self.result[0]
            key_value_change = first_record[key_name]
            for record in self.result:
                if record[key_name]==key_value_change:
                    list_records.append(record)
                else:
                    print list_records
                    self.print_report(list_records)
                    list_records=[]
                    list_records.append(record)
                    print "------------------------------"
                    key_value_change=record[key_name]
        else:
            self.print_report(self.result)
        
#        if (self.cur_report.page_number>0):
#            self.cur_report.bloc_number = 1 
#            self.cur_report.end_page(record)
#======================================================
        
            
        today=datetime.datetime.now()
        time_now=str(today.time())[0:8]
        name_file=report_name+"_"+str(today.date())+"_"+time_now+".json"
        # Write JSON file 
        self.cur_report.to_json(name_file,report)
        id_file_created=self.save_json_file_name(name_file,self. cur_report.report.id)
#        print("file id:",id_file_created)
        
        return [self.cur_report,id_file_created]
    
    def print_report(self,list_record):
        nbr_records_list=len(list_record)
        max_bloc_temp=self.max_bloc_details
        if(nbr_records_list<self.max_bloc_details):
            self.max_bloc_details=nbr_records_list
        
        self.total_record_list+=len(list_record)
        
        for record in list_record:
            
            # process Heard first time
            if self.cur_report.page_number == 0:
                # create a new page
                self.cur_report.new_page(record)
                 
            # process body for any record
            self.cur_report.evaluate_fields('Details',record)
            self.cur_report.bloc_number += 1 
        
            # process footer only after the last bloc  
            #FIXME
            if self.cur_report.bloc_number >  self.max_bloc_details:
                self.cur_report.bloc_number = 1 
                # end of page
                self.cur_report.end_page(record)
                # Create a next page
                if(self.total_record_list<self.total_record_all_list):
                    self.cur_report.new_page(record)
            
                
        self.max_bloc_details=max_bloc_temp
                   
        
    def code_mort(self):
        if cur_report.key_group() != []:      
                
                if self.ref_key_group == None: 
                    self.ref_key_group = cur_key_group
                
                if self.ref_key_group == cur_key_group: 
                    cur_report.evaluate_fields('Details',record)
                    cur_report.bloc_number += 1 
                else:
                    # verifier l'impression des blocs vides
                    cur_report.end_page(record)
                    

    def save_json_file_name(self,name_file,report_id):
        id_file = self.pool.get('report.def.json_files').create(self.cursor, self.user_id, {'name':name_file,'report_id':report_id})
        return id_file
    
    def update_context(self,key_context,val_context):
        self.report_context[key_context] = val_context
        return self.report_context
        
    def get_object_model(self, my_model):
    
        report_pool = self.pool.get(my_model['model'])
        if my_model.has_key('name'):
            id = report_pool.search(self.cursor,self.user_id, [('name','=',my_model['name'])])
        else:
            id = report_pool.search(self.cursor,self.user_id, [('id','=',my_model['id'])])
        
        if id:
            all_objects = report_pool.browse(self.cursor,self.user_id, id)  
            return all_objects[0] 
        else:
            return None 
                     
    
    def raz_totals(self,totals):
        for total in totals:
            self.set_total(total,0)
        return True
    
    def fill_all_json_data(self,json_data):
        json_report = json_data['Report']
        json_pages  =  json_report['Pages']
        my_temple = template(page)
        html_report = my_temple.create_new_report()
        for key_page,my_page in json_pages.items():
            page_number = int(key_page.replace('Page',''))
            my_temple.fill_create_new_page(page_number) 
            for key_section,my_section in my_page.items():
                
                for key_bloc,my_bloc in my_section.items():
                    bloc_number = int(key_page.replace('Bloc',''))
                    for field,value in my_bloc.items():
                        self.fill_field_value(key_section,page_number,bloc_number,field,value)
    
    
    def fill_field_value(self,key_section,page_number,bloc_number,field,value):
        return ' '
                    
                    
           
    def set_path(self,cr,uid,cid,tmpl_path = None, croquis = None):
         
        self.cid = cid
        self.uid = uid 
        
        if tmpl_path == None:
            self.path_template = os.getcwd() + '/openerp/addons/report_def'
            self.folder = 'report_def'  
            self.path_dest = '/var/www/' + self.folder
      
        self.croquis = croquis
        self.src_template = self.path_template + "/" 
        if self.croquis == None:
            self.trg_template =  self.path_dest + "/out/"
            self.url_template =  self.folder + "/out/"
        else:
            self.trg_template =  self.path_template + "/tmp/"
  
            
    
    #===========================================================================
    # def list_to_preview(self,template,res_pool):
    #    file_source = self.src_template + template
    #    if self.create_folder(self.trg_template):
    #        file_target = self.trg_template + template
    #        page = self.open_template(file_source)
    #        str_start = '<label id="'
    #        str_end = '">'
    #        dict_fields = self.page_parse(page,str_start,str_end)
    #        dict_fields = self.load_values(dict_fields,res_pool)
    #        self.replace_values(page,dict_fields,file_target)
    #===========================================================================
    
    
    #===========================================================================
    # def load_values(self,dict_fields,res_pool):
    #    for field_id in dict_fields.values():
    #        ref_field = field_id['ref_field']
    #        field_id_resu = res_pool.get_field_result(ref_field)
    #        for index in field_id_resu.keys():
    #            value = field_id_resu[index]
    #            if value <> None:
    #                field_id['amount'] = value
    #                field_id['str_value'] = ' '
    #                dict_fields[field_id['ref_field']] = field_id 
    #    return dict_fields
    # 
    #===========================================================================




class current_page():
    def __init__(self,cur_report):
        self.my_page = cur_report
        
        
class current_report():
    
    def __init__(self,context):
        
        self.pages = collections.OrderedDict()
        self.totals = {}
        self.images = collections.OrderedDict()
        self.page_number = 0
        self.report = context['report']
        self.form_data = context['datas']
        self.bloc_number = 1
        self.context = context
        self.context['current_report'] = self
        
        self.form_lst_fields = self.form_fields('Form')
        
        self.section_names = { 'Report_header': self.get_section_fields('Report_header'),
                               'Page_header'  : self.get_section_fields('Page_header'),
                               'Details'      : self.get_section_fields('Details'),
                               'Page_footer'  : self.get_section_fields('Page_footer'),
                               'Report_footer': self.get_section_fields('Report_footer'),
                              }    
        
        tot_function = self.total_calculate
        self.total_functions = { 'Count':'count_total',
                                 'Sum':'sum_total',
                                 'Average':'average_total',
                                 }
        self.init_totals()
        self.key_group()
    
    def get_max_bloc_section(self,section_name):
        max_bloc = 1 
        for max_bloc_section in self.report.section_bloc_ids:
            if max_bloc_section.section == section_name:
                max_bloc = max_bloc_section.max_bloc_number
                break
        return max_bloc 
            
        
    
    def init_totals(self):
        '''
         create totals for current report and reset totals for all methods
        '''
        for total in self.report.total_ids:
            my_total = {}
            my_total['name'] = total.name
            my_total['function'] = total.function
            my_total['method'] = self.total_functions.get(total.function,'Sum') 
            my_total['reset_after_print'] = total.reset_after_print
            my_total['reset_repeat_section'] = total.reset_repeat_section
            self.totals[total.name] = self.reset_total(my_total)
            
    def total_calculate(self,field,value):
        total_name = field.total_id.name
        my_total = self.totals[total_name]
        if my_total['function'] == 'Sum':
                
                if(value==None or value==""):
                    value=0
                value=float(value)
                my_total['total'] = my_total['total'] + value
        
        if my_total['function'] == 'Count':
            my_total['total'] = my_total['total'] + 1
        
        if my_total['function'] == 'Average':
            my_total['total'] = (my_total['total'] + value) / 2 
  
        self.totals[total_name] = my_total 
        
    def reset_total(self,my_total):
        '''
        reset totals for given total and a list functions
        '''
        my_total['total'] = 0
        return my_total
      
            
            
            
    def get_section_name(self,section_name):
        if self.section_names.has_key(section_name):
            return self.section_names[section_name]
    
    def field_object(self,field_id, section_name ='Details'):
        lst_fields = self.get_section_name(section_name)
        
    
    
    def number(self):
        return self.page_number
    
    def blocNumber(self):
        return self.bloc_number
    
    def date(self):
        return date.today()
    
    def field_object(self,field_id, section_name ='Details'):
        section_list = self.get_section_fields(section_name)
        if section_list.has_key(field_id):
            field = section_list[field_id]
            return field
    
    def field(self,field_id, section_name ='Details'):
        field = self.field_object(field_id, section_name)
        value = self.get_field(self.page_number, field.section, self.bloc_number, field.name)
        return value
    
    def get_section_fields(self,section_name):
        section_list = {}
        for field in self.report.field_ids:
            if field.section == section_name:
                section_list[field.name] = field
        return section_list
    
    def form_fields(self,type_value):
        lst_fields = []
        for field in self.report.field_ids:
            if field.source_data == type_value:
                lst_fields.append(field)
        return lst_fields
    
    def new_page(self,record):
        self.page_number += 1
        self.evaluate_fields('Report_header',record)
        self.evaluate_fields('Page_header',record)
        
    
    def end_page(self,record):
        self.evaluate_fields('Page_footer',record)
        self.evaluate_fields('Report_footer',record)
    
    
    def replace_form_values(self,str_query):
        
        for parm in self.form_lst_fields:
            str_search = '@form.'+parm.name
            str_value =  "'"+ self.value_from_form(parm.name.rstrip())+"'"
            str_query = str_query.replace(str_search,str_value)
        return str_query
    
    
    def get_page(self,page_number):
        key_page = 'Page' + str(page_number)
        if not (self.pages.has_key(key_page)):
            self.pages[key_page] = collections.OrderedDict()
        return self.pages[key_page]

    def get_page_section(self,page_number,section_name):   
        mypage = self.get_page(page_number) 
        if not (mypage.has_key(section_name)):
            mypage[section_name] = collections.OrderedDict()
        return mypage[section_name]
    
    def get_page_section_bloc(self,page_number,section_name,bloc_number):
        key_bloc = 'Bloc' + str(bloc_number)   
        mysection = self.get_page_section(page_number,section_name) 
        if not (mysection.has_key(key_bloc)):
            mysection[key_bloc] = collections.OrderedDict()
        return mysection[key_bloc]
    
    
    def set_field(self,page_number,section_name,bloc_number,field_id,value): 
        mypage_section_bloc = self.get_page_section_bloc(page_number,section_name,bloc_number)
        mypage_section_bloc[field_id] = value
    
    def get_field(self,page_number,section_name,bloc_number,field_id): 
        mypage_section_bloc = self.get_page_section_bloc(page_number,section_name,bloc_number)
        if mypage_section_bloc.has_key(field_id):
            return mypage_section_bloc[field_id]
        else:
            return ''
    
    def page_get_section_bloc(self,page_number,section_name,bloc_number):
        mypage_section_bloc = self.get_page_section_bloc(page_number,section_name,bloc_number)
        return mypage_section_bloc
    
    def get_value_from_bloc(self,bloc_values,field_id):
        if bloc_values.has_key(field_id):
            return bloc_values.has_key[field_id]
        else:
            return ' '
        
    def to_json(self,file_name,rep):
        report_pages  = collections.OrderedDict()
        myreport = collections.OrderedDict()
        
        report_pages['Pages'] = self.pages 
        report_pages['Images'] = self.images
        myreport['Report'] = report_pages
        path_folder = os.getcwd() + '/openerp/addons/report_def_store/static/reports'
        if self.create_folder(path_folder):
            pass 
        path_folder = path_folder + '/'+ rep.module_id.shortdesc
        if self.create_folder(path_folder):
            path_folder = path_folder + '/'+ self.report.name
            if self.create_folder(path_folder):
                file_name = path_folder + '/' + file_name
                with open(file_name, 'w') as json_file:
                    json.dump(myreport, json_file, indent=4)
        return myreport 
    
    def create_folder(self,path_target):
        try:
            os.mkdir(path_target)
            return True
        except OSError:
            pass
            return True
        
    def key_group(self):
        self.field_key_group = []
        for section_name in self.section_names:
            section_list = self.get_section_fields(section_name)
            for key_name,field in section_list.items():
                if field.group == True:
                    self.field_key_group.append(field.name)
                    print "test key group",field.name
        return self.field_key_group
    
    
    def key_group_value(self,record):
        ref_value = ''
        for field in self.field_key_group:
            print "key_group_value",field
            value = self.load_field_value(field,record)
            ref_value = ref_value + value
        return ref_value
                     
    def evaluate_fields(self,section_name,record):
        
        section_list = self.get_section_fields(section_name)
        mysection_page = self.get_page_section(self.page_number,section_name)
        for key_name,field in section_list.items():
            value = self.load_field_value(field,record)
            self.set_field(self.page_number,field.section,self.bloc_number,field.name,value)
            if field.total_id and field.source_data != 'Total':
                self.total_calculate(field,value)
                
            
        for key_name,field in section_list.items():
            value = self.get_field(self.page_number, field.section, self.bloc_number, field.name)
            value = self.calculate_field_value(field,value)
            self.set_field(self.page_number,field.section,self.bloc_number,field.name,value)
    
    def value_from_model(self,field,record):
        if record.has_key(field.name):
            return record[field.name]
        else:
            return 'error field' + field.name
    
    def value_from_form(self,field_id):
        if self.form_data.has_key(field_id):
            return self.form_data[field_id]
        else: 
            return 'error form data' + field_id
    
    def value_from_total(self,field):
        value = ''
        if field.total_id:
            my_total = self.totals[field.total_id.name]
            value = my_total['total']
            if my_total['reset_after_print']:
                self.totals[my_total['name']] = self.reset_total(my_total)
                
        return value
    
    
    def load_field_value(self,field,record):
        value = ''
        if field.source_data == 'Model':
            value = self.value_from_model(field,record)
            
        if field.source_data == 'Form':
            value = self.value_from_form(field.name)
        
        if field.source_data == 'Total':
            value = self.value_from_total(field)
            
        return value
    
    
    def field_static_image(self,field,value):
        
        if field.field_type == 'Static Image':
            if not self.images.has_key(field.name): 
                self.images[field.name] = value
            value = 'StaticImage'
            
        return value
       
    def calculate_field_value(self,field,value):

        if field.source_data == 'Function':
            value = 'my_function'
        
        if field.source_data == 'Computed':
            value = eval(field.expression,self.context)
        
        if field.source_data == 'Html':
            value = 'my_html'
        
        value = self.field_static_image(field,value)
        return value

        
#class html_template():  
#    
#    def __init__(self,page):
#        self.html_page = page
#        self.start_section = self.parse_html_section('<!DOCTYPE html>','report_')
#        self.report_header = self.parse_html_section('<header class="Report_header">','</header>')
#        self.page_header = self.parse_html_section('<header class="Page_header">','</header>')
#        self.details = self.parse_html_section('<section class="Details">','</section>')
#        self.page_footer = self.parse_html_section('<footer class="Page_footer">','/footer')
#        self.report_footer = self.parse_html_section('<footer class="Report_footer">','</footer>')
#        
#    def parse_html_section(self,start_balise,end_balise): 
#        # recherche du code Html dans une balise html
#        start = 0
#        fin   = len(self.html_page)
#        pos   =  self.html_page.find(start_balise,start,fin)
#        html_section = ""
#        if pos>0: 
#            start  =  pos + len(start_balise)+1
#            endpos = page.find(end_balise,start,fin)
#            if endpos>0:
#                html_section = page[pos + len(str_start):endpos+len(end_balise)]
#            else:
#                print "sans balise de fin"
#            
#        return html_section
#    
#    
#           

#class htmlparser():
#    def __init(self,template):
#        self.trg_template = ''
#        self.src_template = ''
#        self.template = template
#        self.dico = {}
#        
#    def set_action(self,begin_str,end_str):
#        dico[begin] = end_str
#        
#    def open_template(self,myfile):
#        page = urllib.urlopen(myfile).read()
#        return page
#    
#    def page_parse(self,page,str_start,str_end):
#        start = 0
#        fin = len(page)
#        occur = 0  
#        report_field = {}
#        dict_fields = {}
#        while start <= fin:
#            pos =  page.find(str_start,start,fin)
#            if pos>0: 
#                start =  pos + len(str_start)+1
#                endpos = page.find(str_end,start,fin)
#                if endpos>0:
#                    occur = occur + 1
#                    start_field = pos + len(str_start)
#                    field_id = page[start_field:endpos]
#                    report_field = {}
#                    dict_fields[field_id] = ' ' 
#                else:
#                    print "erreur fichier"
#            else:
#                start = fin+1
#                
#        return dict_fields
#    
#        
#    def load_page(self):
#        file_source = self.src_template + template
#        if self.create_folder(self.trg_template):
#            file_target = self.trg_template + template
#            page = self.open_template(file_source)
#            str_start = '<label id="'
#            str_end = '">'
#            dict_fields = self.page_parse(page,str_start,str_end)
#            dict_fields = self.load_values(dict_fields,res_pool)
#            self.replace_values(page,dict_fields,file_target)
#    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
