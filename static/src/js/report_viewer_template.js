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
            this.model = new instance.web.Model('web_example.stopwatch');
           
        },
	to_print:function(){
	    window.print();	
	},
	to_pdf:function(){
	   
	    var Partners = new instance.web.Model('report.def');
	    Partners.call('hello_func',[$("#viewer").html()],undefined,{ shadow:true })
	    .fail(function(datas){
		    alert('erreur');
		})
		.done(function(datas){
		    console.log(datas);
		});
		
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
       		$(".banner_printer").hide();
       		var viewerpdf = document.getElementById('viewer');
			var height_div=screen.height-130;
			viewerpdf.style.height = height_div+"px";
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
