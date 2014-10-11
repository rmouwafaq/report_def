# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as soup
from xhtml2pdf import pisa
import copy

class Template(object):
    def __init__(self,src_path=None):
        self.content_html=None
        self.report_template=None
        
        if(src_path):
            self.content_html=self.read(src_path)
            self.report_template=self.content_html.find(attrs={"class":"Page"})
            
    def read(self,src_path):
        with open(src_path, 'r+') as template_file:
            self.file_content=template_file.read()
        self.content_html=soup(self.file_content)
        self.report_template=self.content_html.find(attrs={"class":"Page"})
    def set_content_html(self,page_content):
        self.content_html=soup(page_content)
        self.report_template=self.content_html.find(attrs={"class":"Page"})        
        
    def copie(self,dest_path):
        with open(dest_path, 'w+') as template_file:
            template_file.write(self.content_html.encode("utf-8"))
    def save_pdf(self,outputFilename):
        resultFile = open(outputFilename, "w+b")
        pisaStatus = pisa.CreatePDF(self.content_html,dest=resultFile)  
        resultFile.close() 
        return pisaStatus.err
    
    def get_format(self):
        report=self.content_html.find(id="Report")
        return report["format"]
    
    def get_section(self,section_name):
        return self.report_template.find(attrs={"class":section_name})
    
    def get_ids_section(self,section_name):
        section_tag=self.get_section(section_name)
        ids=[]
        for element in section_tag.find_all(id=True):
            ids.append(element['id'])
        return ids
        
    def get_class_section(self,section_name,class_name):
        section_tag=self.get_section(section_name)
        return section_tag.find_all(attrs={"class":class_name})
        
    def get_all_ids(self):
        ids=[]
        for element in self.report_template.find_all(id=True):
            ids.append(element['id'])
        return ids
        
    def get_element_tag(self,tag_name):
        return self.report_template.find_all(tag_name)
    
    def get_element_id(self,id_name):
        return self.report_template.find(id=id_name)
    
    def get_element_class(self,class_name):
        return self.report_template.find_all(attrs={'class':class_name})
        
    def get_element_attribute(self,attribute_name,attribute_value):
        return self.report_template.find_all(attrs={attribute_name:attribute_value})
        
    def get_value_element(self,element):
        return element.string
    
    def set_value_element(self,element,value):
        element.string=value
        
    def get_repeted_bloc(self):
        return copy.deepcopy(self.report_template.find(attrs={"type":"repeted_bloc"}))
    def get_ids_repeted_bloc(self):
        ids=[]
        repeted_bloc=self.report_template.find(attrs={"type":"repeted_bloc"})
        for id_cellule in repeted_bloc.find_all(id=True):
            ids.append(id_cellule['id'])
        return ids
     
    def get_max_bloc(self,bloc_repeted):
        return bloc_repeted['max_bloc']
        
    def get_footer_bloc(self,bloc_repeted):
        class_name=bloc_repeted['footer_bloc']
        return self.report_template.find(attrs={"class":class_name})
    
    def get_tag_head(self):
        tag_head=copy.deepcopy(self.content_html.find("head"))
        return tag_head
   
        
    def is_multi_page(self):
        if(self.report_template.find(attrs={"type":"repeted_bloc"}).clear()):
            return True
        return False
    
    def duplicate_page(self,count_page):
        modele_page=copy.deepcopy(self.content_html.find(attrs={"class":"Page_container"}))
        self.content_html.find(id="Report").clear()
        for i in xrange(0,count_page,1):
            self.content_html.find(id="Report").append(copy.deepcopy(modele_page))
            self.content_html.find(id="Report").append(self.content_html.new_tag("br"))
        
    def duplicate_bloc(self,page_index,count_bloc,modele_bloc,footer_bloc=None):
        pages=self.content_html.find_all(attrs={"class":"body_table"})
        pages[page_index].clear()
        for i in xrange(0,count_bloc,1):
            mb=copy.deepcopy(modele_bloc)
            pages[page_index].append(mb)
            del mb
        if(footer_bloc!=None):
            pages[page_index].append(copy.deepcopy(footer_bloc))
        if(self.content_html.find(attrs={"class":"pagination"})):
            pag=self.content_html.find_all(attrs={"class":"pagination"})
            if(pag[page_index]):
                pag[page_index].string=str(page_index+1)
    def set_val_bloc_repeted(self,page_index,values_id):
        pages=self.content_html.find_all(attrs={"class":"Page"})
        blocs_page=pages[page_index].find_all(attrs={"type":"repeted_bloc"})
        k=1
        
        for key,value in values_id.iteritems():
            for id_bloc in blocs_page[key].find_all(id=True):
                if(value.has_key(id_bloc['id'])):
                    id_bloc.string=str(value[id_bloc['id']]) 
    def set_values_section(self,page_index,section_name,values_id):
        pages=self.content_html.find_all(attrs={"class":"Page"})
        section=pages[page_index].find(attrs={"class":section_name})
        
        for key,value in values_id.iteritems():
            if(section.find(id=key)):
                if(section.find(id=key).name=="img"):
                    tag_img=section.find(id=key)
                    tag_img["src"]="data:image/jpeg;base64,"+str(value)
                else:
                    section.find(id=key).string=str(value).encode("utf-8")
            