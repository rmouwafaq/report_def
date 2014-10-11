openerp.report_def = function (instance) {
	var _reports_link="report_def_store/static/reports/";
    instance.web.client_actions.add('report.viewer.action', 'instance.report_def.Action');
    instance.report_def.Action = instance.web.Widget.extend({
        template: 'report_viewer_template.action',
        events: {
	    'mouseover .banner_printer': 'opacity_mouse_in',
	    'mouseout .banner_printer': 'opacity_mouse_out',
	    'click #to_pdf': 'to_pdf',
	    'click #to_print': 'to_print',
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
	opacity_mouse_in:function(){
	    $(".banner_printer").css({'opacity':'1','border':'1px solid rgb(254,29,63)','border-top':'none'});	
	},
	opacity_mouse_out:function(){
	    $(".banner_printer").css({'opacity':'0.3','border':'none'});	
	},
       getData:function(){
        		
        		var json_file;
			var query_string=document.location.href.split("#")[1];
			query_string=query_string.split("&");
			var json_file_id=query_string[0].split("=")[1];
			var report_id=query_string[1].split("=")[1];
			this.fetch("report.def.json_files",['name'],[['id','=',json_file_id]]).then(function(filesname){
	        		_.each(filesname,function(jsonfile){
	        				json_file=jsonfile.name;
	        			});
        		});
        		this.fetch("report.def",['name','template_html','json_file_name','module_id'],[['id','=',report_id]]).then(function(reports){
				
	        		_.each(reports,function(report){
						
	        				var module_name=report.module_id[1];
	        				$("#viewer").html(report.template_html);
	        				json_file=_reports_link+module_name+"/"+report.name+"/"+json_file;
	        				
	        			});
				
				
        		}).then(function(){
        			engine_report(json_file,"#Report");
        			format_rapport=$("#Report").attr("format");
  			  	page_format(format_rapport);
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
