function engine_report(template_content, target){
	    //Loading html file using Ajax 
	    //$.get(template_path_name,function(data){
			
			content_html=$('<div>'+template_content+'</div>');
			content_html.find("meta").remove();

			$("#viewer").html(content_html.html());	
			 
			
		
	      //}).then(function(){
		//get invisible data in page_footer and put them in footer of table in section details
		 $(".Page_footer").each(function( index ) {
			$(this).find("div[data-type='footer_data']").each(function( index2 ) {
				var valeur=$(this).html();
			
				$(".Details:eq("+index+") td[class="+$(this).attr("id")+"]").text(valeur);
				$( ".Page_footer:eq("+index+") div" ).remove( "#"+$(this).attr("id") );
		        });
		   	
		 });
		 $("table").attr('cellspacing','0');
		 $("table").attr('cellpadding','0');
		 format_tags(target+" *");		
		//});

	
	
   
	
}


// format and parsing value of tags in deffirent types(integer,double...)
function format_tags(targets_parent){
	function get_case(elem){
	       //var text=$(elem).text().replace(/^\s+|\s+$/g,'');
	       var text=$(elem).text().trim();
	       var max_case=$(elem).attr("data-max-case");
	       var com=0;
	       var type_case="input_char_barre";
	       if($(elem).attr("data-type-case")=="slash"){
		  type_case="input_char_slash";
	       }
	       var show_text="<table class='tableau0 "+type_case+"' cellspacing='0'><tr>";
	       if(type_case=="input_char_slash"){
		  show_text+="<td></td>";
	       } 
	       for(i=0;i<max_case;i++){
		  show_text+="<td>";
		  if(i<text.length){
		     if(text[i]=="?"){
			show_text+=" ";
		     }else{
			show_text+=text[i];
		     }
		  }
		  
		  show_text+="</td>";
	       }
	       show_text+="</tr></table>";
	       
	       $(elem).html(show_text);
	       
	       $(elem).find("td").css('font-size',$(elem).attr("data-size")+'px');
	       
	       if(type_case=="input_char_barre"){
		  var w=$(elem).attr("data-width");
		  var h=$(elem).attr("data-height");
		  $(elem).find(".input_char_barre td").css({'width':w+'px','height':h+'px'});
		  
	       }
		
	       if(type_case=="input_char_slash"){
		  
		   var w=$(elem).attr("data-width");
		    
		   var h=$(elem).attr("data-height");
		   
		   var back_w=parseInt(w)+8;
		   var back_h=parseInt(h)+3;
		   var f_back_w=w/4;
		   var f_back_h=parseInt(h)+7;
		   $(elem).find(".input_char_slash td").css({'width':w+'px','height':h+'px','background-size':back_w+'px '+back_h+'px'});
		   $(elem).find(".input_char_slash td:first-child").css({'background-size':f_back_w+'px '+f_back_h+'px'});
	       }
	 }
	 $(".zone_case").each(function( index ) {
	       var text=$(this).text().replace(/^\s+|\s+$/g,''); 
	       var nbr_chars=text.length;
	       var max_case=parseInt($(this).attr("data-max-case"));
	       var data_align="LTR";
	      
	       if($(this).attr("data-align")!=undefined){
		  data_align=$(this).attr("data-align");
	       }

	       var com=0;
	       var type_case="input_char_barre";
	       if($(this).attr("data-type-case")=="slash"){
		  type_case="input_char_slash";
	       }
	       var show_text="<table class='tableau0 "+type_case+"' cellspacing='0'><tr>";
	       if(type_case=="input_char_slash"){
		  show_text+="<td></td>";
	       } 
	       for(i=0;i<max_case;i++){
		  show_text+="<td>";
		  if(data_align=="RTL"){
			
			if(i>=max_case-nbr_chars){
				show_text+=text[i-(max_case-nbr_chars)];
			}
		  }else{
			if(i<nbr_chars){
				show_text+=text[i];
			}
		  }
		  
		  show_text+="</td>";
	       }
	       show_text+="</tr></table>";
	       
	       $(this).html(show_text);
	       
	       $(this).find("td").css('font-size',$(this).attr("data-size")+'px');
	       
	       if(type_case=="input_char_barre"){
		  var w=$(this).attr("data-width");
		  var h=$(this).attr("data-height");
		  $(".zone_case .input_char_barre td").css({'width':w+'px','height':h+'px'});
		  
	       }
		
	       if(type_case=="input_char_slash"){
		 
		   var w=$(this).attr("data-width");
		    
		   var h=$(this).attr("data-height");
		   
		   var back_w=parseInt(w)+8;
		   var back_h=parseInt(h)+3;
		   var f_back_w=w/4;
		   var f_back_h=parseInt(h)+7;
		  
		   $(this).find(".input_char_slash td").css({'width':w+'px','height':h+'px','background-size':back_w+'px '+back_h+'px'});
		   
		   $(this).find(".input_char_slash td:eq(0)").css({'background-size':f_back_w+'px '+f_back_h+'px','width':'5px'});
	       }
	 });
	 
	 $(".zone_date").each(function( index ) {
	    var date_val=$(this).text().trim();
	    console.log("text1:::"+date_val);
	    var separ_case=$(this).attr("data-separator-case");
	    var date_sep="";
	    
	    if(date_val.indexOf("/")!="-1"){
	       date_sep="/";
	    }
	    if(date_val.indexOf("-")!="-1"){
	       date_sep="-";
	    }
	    
	    var split_date=date_val.split(date_sep);
	    $(this).empty();
	    var case_value="";
	    var width_dots="20";
	    for(var i=0;i<split_date.length;i++){
	      if($(this).attr("data-type-case")=="dots"){
		if(split_date[i]=="??" || split_date[i]=="????" ){
			case_value+="&nbsp;";
			
		}else{
			case_value=split_date[i];
		}
		if(split_date[i].length==4){
			width_dots=parseInt($(this).attr("data-width"))*2;
		}else{
			width_dots=$(this).attr("data-width");
		}
		$(this).html($(this).html()+"<div class='zone_point1' style='width:"+width_dots+"px;font-size:"+$(this).attr("data-size")+"' >"+case_value+"</div>");
		if(i<split_date.length-1){
			$(this).html($(this).html()+"<strong>/</strong>");
		}
	      }else{
		$(this).html($(this).html()+"<div class='zone_case' data-max-case='"+split_date[i].length+"'  data-type-case='"+$(this).attr("data-type-case")+"' data-size='"+$(this).attr("data-size")+"' data-width='"+$(this).attr("data-width")+"' data-height='"+$(this).attr("data-height")+"'>"+split_date[i]+"</div>");
		if(i<split_date.length-1){
		 $(this).html($(this).html()+"&nbsp;<b style='font-size:"+(parseInt($(this).attr("data-size"))*2)+"px;'>"+separ_case+"</b>&nbsp;");
		}
		
		get_case($(this).find(".zone_case:eq("+i+")"));
		if($(this).attr("data-type-case")=="slash"){
		    $(this).find(".zone_case table td:first-child").css('width','2px');
		}
	      }
	    }
	    
	  
	    
	 });
	 
	 $(".nombre").each(function( index ) {
		var val_text=$(this).text().replace(/^\s*|\s*$/,'');
		var split_value=val_text.split(".");
		var part_int;
		var part_decimal;
		if(split_value.length==2){
			part_int=split_value[0];
			part_decimal=split_value[1];
		}else{
			part_int="  ";
			part_decimal="  ";
		}
		$(this).empty();
		
		var int_part_html="<table class='chiffre' cellspacing='0'><tr>";
		//int part
		for( var i=0;i<$(this).attr("data-int-max")-part_int.length;i++){
			int_part_html+="<td style='width:20px;'>&nbsp;</td>";
		}
		for(var i=0;i<part_int.length;i++){
			int_part_html+="<td style='width:20px;'>"+part_int[i]+"</td>";
		}
		int_part_html+="</tr></table><table class='comma' cellspacing='0'><tr><td style='font-size:12px'>.</td></tr></table>";
		
		//decimal part
		var decimal_part_html="<table class='chiffre'  cellspacing='0'><tr>";
		for(var i=0;i<part_decimal.length;i++){
			
			decimal_part_html+="<td style='width:20px'>"+part_decimal[i]+"</td>";
		}
		decimal_part_html+="</tr></table>";
		$(this).html($(this).html()+int_part_html+decimal_part_html);
	 });

	 $(".zone_check").each(function( index ) {
	    var check_val=$(this).text().replace(/^\s*|\s*$/,'');
	    var check_type="2d";
	    if($(this).attr("data-type")){
	       check_type=$(this).attr("data-type");
	    }
	    
	    if(check_type=="3d"){
	       $(this).addClass("zone_check_3d");
	    }
	    if(check_val=="True" || check_val=="true" || check_val=="1" || check_val=="yes" || check_val=="x" || check_val=="X"){
	       $(this).text("x");
	    }else{
	       $(this).empty();
	    }
	 });
}
// add tag <link> of css according to format of pages (portrait or landscape)
function page_format(format){
	
	var link = document.createElement('link');
	link.setAttribute('rel', 'stylesheet');
	link.setAttribute('type', 'text/css');
	if(format=="landscape"){
		link.setAttribute('href', 'report_def/static/lib/inclu/style_landscape.css');
	}else{
		link.setAttribute('href', 'report_def/static/lib/inclu/style_portrait.css');
	}
	link.setAttribute('media', 'all');
	
	document.getElementsByTagName('head')[0].appendChild(link);
}
