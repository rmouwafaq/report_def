openerp.report_def = function (instance) {
	var _reports_link = "report_def/static/reports/";
	var zoom=100;
    instance.web.client_actions.add('report.viewer.action', 'instance.report_def.Action');
    instance.report_def.Action = instance.web.Widget.extend({
        template: 'report_viewer_template.action',
        events: {
	    'mouseover .banner_printer': 'opacity_mouse_in',
	    'mouseout .banner_printer': 'opacity_mouse_out',
	    'click #to_pdf': 'to_pdf',
	    'click #to_print': 'to_print',
	    'click #zoom_back': 'zoom_back',
	    'click #zoom_forward': 'zoom_forward',
        },
        init: function () {
            this._super.apply(this, arguments);
	    console.log('arguments',arguments);
            this._start = null;
            this._watch = null;
            //this.model = new instance.web.Model('web_example.stopwatch');
           
        },
	to_print:function(){
	    window.print();	
	},
	to_pdf:function(){
	   
	    
		
	},
	zoom_back:function(){
	  if(zoom>25){  
	    zoom=zoom-25;
	    $("#Report").css('zoom',zoom+'%');	
	  }
	},
	zoom_forward:function(){
	  if(zoom<200){  
	    zoom=zoom+25;
	    $("#Report").css('zoom',zoom+'%');	
	  }
	},
	opacity_mouse_in:function(){
	    $(".banner_printer").removeClass("banner_hover_out");
	    $(".banner_printer").addClass("banner_hover_in");	
	},
	opacity_mouse_out:function(){
	    $(".banner_printer").removeClass("banner_hover_in");	
	    $(".banner_printer").addClass("banner_hover_out");
	},
    getData:function(){
       		
    		/*var template_path_name="";
    		
			var query_string=document.location.href.split("#")[1];
			query_string=query_string.split("&");
			var report_id=query_string[1].split("=")[1];
			
			var viewer_type="html";
			var data_file_pdf="";
			
    		this.fetch("report.def",['name','module_id','template_file_name','out_template_file_name'],[['id','=',report_id]]).then(function(reports){
			
        		_.each(reports,function(report){
					
        			var module_name=report.module_id[1];
					var file_name="";
					if(report.out_template_file_name==undefined ){
						file_name=report.template_file_name;
					}else{
						file_name=report.out_template_file_name;
					}
					template_path_name=_reports_link+module_name+"/"+report.name+"/HTML/"+file_name;
        				
        		});
			
			
    		}).then(function(){
    			if(viewer_type=="html"){
        			engine_report(template_path_name,"#Report");
        			format_rapport=$("#Report").attr("format");
  			  		page_format(format_rapport);
  			  	}else{
  			  		$(".banner_printer").hide();
  			  		
  			  		$("#viewer #pdfviewer").attr("src","data:application/pdf;base64," + data_file_pdf);
  			  	}
    		});*/
			
			function base64Encode(str) {
			    var CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
			    var out = "", i = 0, len = str.length, c1, c2, c3;
			    while (i < len) {
			        c1 = str.charCodeAt(i++) & 0xff;
			        if (i == len) {
			            out += CHARS.charAt(c1 >> 2);
			            out += CHARS.charAt((c1 & 0x3) << 4);
			            out += "==";
			            break;
			        }
			        c2 = str.charCodeAt(i++);
			        if (i == len) {
			            out += CHARS.charAt(c1 >> 2);
			            out += CHARS.charAt(((c1 & 0x3)<< 4) | ((c2 & 0xF0) >> 4));
			            out += CHARS.charAt((c2 & 0xF) << 2);
			            out += "=";
			            break;
			        }
			        c3 = str.charCodeAt(i++);
			        out += CHARS.charAt(c1 >> 2);
			        out += CHARS.charAt(((c1 & 0x3) << 4) | ((c2 & 0xF0) >> 4));
			        out += CHARS.charAt(((c2 & 0xF) << 2) | ((c3 & 0xC0) >> 6));
			        out += CHARS.charAt(c3 & 0x3F);
			    }
			    return out;
			}
			
			var query_string=document.location.href.split("#")[1];
			console.log("query_string",query_string);   
			query_string=query_string.split("&");
			var report_request_id=query_string[0].split("=")[1];
			
			var viewer_type="html";
			var report_request_bin;
			console.log("report_request_id",report_request_id);
			this.fetch("report.request.view",[],[['id','=',parseInt(report_request_id) ]]).then(function(reports){
				
	        		_.each(reports,function(report){
						
	        			report_request_bin=report.file_request;
	        			viewer_type= report.viewer_type;
	        			
	        				
	        		});
				
				
	    	}).then(function(){
	    			if(viewer_type=="html"){
	    				var str_report_request= base64Encode(report_request_bin);
	        			console.log(atob(str_report_request));
	        			engine_report(atob(str_report_request),"#Report");
	        			
	        			format_rapport=$("#Report").attr("format");
	  			  		page_format(format_rapport);
	  			  	}else{
	  			  		$(".banner_printer").hide();
			       		var viewerpdf = document.getElementById('viewer');
						var height_div=screen.height-130;
						viewerpdf.style.height = height_div+"px";
	  			  		$("#viewer #pdfviewer").attr("src","data:application/pdf;base64," + report_request_bin);
	  			  	}
    		});
			
        		 
		},
		
        fetch:function(model,fields,domain,ctx){
        	return new instance.web.Model(model).query(fields).filter(domain).context(ctx).all();
        },
      
        start: function () {
        	
		this.getData();
        },
        current: function () {
           
        },
        destroy: function () {
            if (this._watch) {
                clearInterval(this._watch);
		
            }
            this._super();
        }
    });
};
