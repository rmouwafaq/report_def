openerp.report_def = function (instance) {
	var zoom=100;
	var state_thumbnails= false;
	var load_thumnails_pages=false;
	var report_request_id;
    instance.web.client_actions.add('report.viewer.action', 'instance.report_def.Action');
    instance.report_def.Action = instance.web.Widget.extend({
        template: 'report_viewer_template.action',
        events: {
        'click #home-link': 'home',
	    'click #to_pdf': 'to_pdf',
	    'click #to_print': 'to_print',
	    'click #zoom_back': 'zoom_back',
	    'click #zoom_forward': 'zoom_forward',
	    'click #fullscreen': 'fullscreen',
	    'click #mode-large': 'mode_large',
	    'click #mode-normal': 'mode_normal',
	    'click #thumbnails': 'thumbnails_pages',
	    'change #bookmarks':'get_bookmark',
        },
        init: function () {
            this._super.apply(this, arguments);
	    	console.log('arguments',arguments);
	    	
	    	this.active_id=arguments[1].context.active_id;
	    	console.log("active id is =",this.active_id);
	    	if(this.active_id == undefined){
	    		this.active_id=arguments[1].params.active_id;
	    	}
	    	this.active_model=arguments[1].context.active_model;
	    	console.log("active id is =",this.active_model);
	    	this.active_action=arguments[1].context.params.action;
            this._start = null;
            this._watch = null;
            
           
        },
    home:function(){
	    //document.location.href="/web#id=" + this.active_id + "&view_type=form&model=" + this.active_model + "&action=" + this.active_action;
	    history.back();	
	},
	to_print:function(){
	    window.print();	
	},
	to_pdf:function(){
	   
	  /*  var doc = new jsPDF();          
		var elementHandler = {
		  '#ignorePDF': function (element, renderer) {
		    return true;
		  }
		};
		var source = window.document.getElementsByTagName("body")[0];
		doc.fromHTML(
		    source,
		    15,
		    15,
		    {
		      'width': 180,'elementHandlers': elementHandler
		    });
		
		doc.output("dataurlnewwindow");*/
		
		new instance.web.Model('report.request.view').call('report_to_pdf',[parseInt(report_request_id)],undefined,{ shadow:true })
			 .then(function(report_info){
			 	alert(report_info);
			 	return report_info;
			 });
		
		
	},
	zoom_back:function(){
	  if(zoom>25){  
	    zoom=zoom-25;
	    $("#Report").css('zoom',zoom+'%');
	    $("#resolution-text").val(zoom+' %');	
	  }
	},
	zoom_forward:function(){
	  if(zoom<200){  
	    zoom=zoom+25;
	    $("#Report").css('zoom',zoom+'%');
	    $("#resolution-text").val(zoom+' %');	
	  }
	},
	
	fullscreen:function(){
	 	var el = document.documentElement
    	, rfs = // for newer Webkit and Firefox
           el.requestFullScreen
        || el.webkitRequestFullScreen
        || el.mozRequestFullScreen
        || el.msRequestFullscreen
		;
		if(typeof rfs!="undefined" && rfs){
		  rfs.call(el);
		} else if(typeof window.ActiveXObject!="undefined"){
		  // for Internet Explorer
		  var wscript = new ActiveXObject("WScript.Shell");
		  if (wscript!=null) {
		     wscript.SendKeys("{F11}");
		  }
		}
	},
	mode_large:function(){
	  $(".oe_leftbar").css('display','none');
	  $("#mode-large").hide();
	  $("#mode-normal").show();
	  $("#screen-option").removeClass("to-right");
	  $("#screen-option").addClass("to-left");
	  
	  $("#zoom-option").removeClass("to-right");
	  $("#zoom-option").addClass("to-center");
	},
	mode_normal:function(){
	  $(".oe_leftbar").css('display','table-cell');
	  $("#mode-normal").hide();
	  $("#mode-large").show();
	  $("#screen-option").removeClass("to-left");
	  $("#screen-option").addClass("to-right");
	  
	  $("#zoom-option").removeClass("to-center");
	  $("#zoom-option").addClass("to-right");
	},
	thumbnails_pages:function(){
		
		if(state_thumbnails){
			$("#thumbnails-pages").removeClass("active-thumbnails");
			$("#thumbnails-pages").addClass("disabled-thumbnails");
			state_thumbnails=false;
		}else{
			$("#thumbnails-pages").removeClass("disabled-thumbnails");
			$("#thumbnails-pages").addClass("active-thumbnails");
			state_thumbnails=true;
			/*var page_thumnails = "<div class='page-thumbnails' ></div>";
			if(load_thumnails_pages==false){
				$(".Page").each(function(index) {
				  $("#thumbnails-pages").html($("#thumbnails-pages").html() + page_thumnails);
				});
				load_thumnails_pages=true;
			}*/
		}
	},
	get_bookmark:function(){
		var id = "#"+$("#bookmarks option:selected").val();
	    var offset = $(id).offset().top ;
	    $('html,.openerp').animate({scrollTop: offset}, 'slow'); 
	    return false; 
	},
    getData:function(){
       		
    		
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
			
			function b64_to_utf8( str ) {
			    return decodeURIComponent(escape(window.atob( str )));
			}

			
			var query_string=document.location.href.split("#")[1];
			console.log("query_string",query_string);   
			query_string=query_string.split("&");
			report_request_id=query_string[0].split("=")[1];
			
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
	    				
	        			var content_report="";
	        			
	        			try{
	        				//content_report=atob(report_request_bin);
	        				content_report=b64_to_utf8(report_request_bin);
	        			}catch(e){
	        				var str_report_request= base64Encode(report_request_bin);
	        				content_report=atob(str_report_request);
	        			}
	        			$("#viewer").addClass("viewer-padding");
	        			engine_report(content_report,"#Report");
	        			
	        			format_rapport=$("#Report").attr("format");
	  			  		page_format(format_rapport);
	  			  		list_bookmarks = "";
	  			  		$(".Page_container").each(function(index) {
						  book_marks = $(this).attr("id");
						  if(book_marks != undefined){
						  	target_name = book_marks.split('_').join(' ');
						  	list_bookmarks += "<option value='"+ book_marks +"'>" + target_name + "</option>";
						  }
						});
	  			  		$("#bookmarks").html(list_bookmarks);
	  			  		
	  			  	}else{
	  			  		$(".banner_printer").hide();
			       		var viewerpdf = document.getElementById('viewer');
						var height_div=screen.height-130;
						viewerpdf.style.height = height_div+"px";
	  			  		$("#viewer").removeClass("viewer-padding");
	  			  		$("#viewer").html("<embed id='pdfviewer' width='100%' height='100%' name='plugin' type='application/pdf' src='data:application/pdf;base64," + report_request_bin +"'  />");
	  			  	}
	  			  	
    		});
			
        		 
		},
		
        fetch:function(model,fields,domain,ctx){
        	return new instance.web.Model(model).query(fields).filter(domain).context(ctx).all();
        },
      
        start: function () {
        	$("#mode-normal").hide();
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
