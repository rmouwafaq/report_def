$(document).ready(function(){
	
    $("table").attr('cellspacing','0');
    $("table").attr('cellpadding','0');
    
    format_tags("*");
    format_rapport=$("#Report").attr("format");
    page_format(format_rapport);
    
  	
  
});

function lisibilite_nombre(nbr)
{
		var nombre = ''+nbr;
		var retour = '';
		var count=0;
		for(var i=nombre.length-1 ; i>=0 ; i--)
		{
			if(count!=0 && count % 3 == 0)
				retour = nombre[i]+' '+retour ;
			else
				retour = nombre[i]+retour ;
			count++;
		}
		
		return retour;
}

function IsNumeric(input)
{
    return (input - 0) == input && (''+input).replace(/^\s+|\s+$/g, "").length > 0;
}

function format_tags(targets_parent){
		$(targets_parent+"[calculated]").each(function( index ) {
                    	var calc=$(this).attr("calculated").split(";");
			var val1=calc[0].split(":")[1];
			var val2=calc[1].split(":")[1];
			var oper=calc[2].split(":")[1];
			var result=0;

			if(oper=="+"){
				result=parseFloat($(val1).text())+parseFloat($(val2).text());
			}
			if(oper=="-"){
				result=parseFloat($(val1).text())-parseFloat($(val2).text());
			}
			if(oper=="*"){
				result=parseFloat($(val1).text())*parseFloat($(val2).text());
			}
			if(oper=="/"){
				result=parseFloat($(val1).text())/parseFloat($(val2).text());
			}

			$(this).text(result);
                });
//-------------------------------------------------------Format type tags-----------------------------------------//
		//Type= text
		$(targets_parent+"[type='text']").each(function( index ) {
                    $(this).css({'padding-left':'5px','font-family':'calibri','text-align':'left'});
                });
               // Type= date
        $(targets_parent+"[type='date']").each(function( index ) {
				if($(this).text()){
		                    $(this).css({'padding-left':'5px','font-family':'calibri','text-align':'left'});
		                    
		                    var d= new Date($(this).text());
		                    var dt= [d.getDate(),d.getMonth()+1, d.getFullYear()].join('/');
		                    $(this).text(dt);
				    if($(this).text()=="NaN/NaN/NaN"){
					$(this).empty();
				    }
                 }
                });
               // Type= datetime
               $(targets_parent+"[type='datetime']").each(function( index ) {
		    if($(this).text()){
		            $(this).css({'padding-left':'5px','font-family':'calibri','text-align':'right'});
		            var time=$(this).text().split(" ");
		            if(time.length==1){
		                time=" ";
		            }else{
		               time=time[1];
		            }
		            
		            var d= new Date($(this).text());
		            var dt= [""+d.getDate(),""+d.getMonth()+1,""+ d.getFullYear()].join('/');
		            $(this).text(dt+" "+time);
			    if($(this).text()=="NaN/NaN1/NaN"){
				$(this).empty();
			    }
			}
                    
                });
               // Type= integer
               $(targets_parent+"[type='integer']").each(function( index ) {
                    $(this).css({'padding-right':'5px','font-family':'calibri','text-align':'right'});
		    if(IsNumeric($(this).text())){
			    var number=parseInt($(this).text());
			    $(this).text(lisibilite_nombre(number));
			    if($(this).text()=="NaN"){
				$(this).empty();
			    }
		    }
		   else{
			    $(this).css({'color':'blue'});
		   }
                });
               
               // Type= double
               $(targets_parent+"[type='double']").each(function( index ) {
		if($(this).text()){
                    $(this).css({'padding-right':'5px','font-family':'calibri','text-align':'right'});
                    var isbolder=$(this).attr("bolder");
                    if(isbolder){
                        $(this).css('font-weight','bolder');
                    }else{
                        $(this).css('font-weight','none');
                    }
                    var precision=2;
                    if(IsNumeric($(this).text())){
			    var val_prec=$(this).attr("precision");

			    if(val_prec){
		                precision=val_prec;
		            }
		            var number=parseFloat($(this).text());
			    number=number.toFixed(precision)
			    //$(this).text(lisibilite_nombre(number));
			    $(this).text(number);
			    if($(this).text()=="NaN"){
				$(this).empty();
			    }
		   }
		   else{
			    $(this).css({'color':'green'});
		   }
		}
		
                });
               // Type= total
               $(targets_parent+"[type='total']").each(function( index ) {
                    if($(this).text()){
			    $(this).css({'padding-right':'5px','font-family':'calibri','text-align':'right','font-weight':'bolder'});
		            
		            var precision=2;
			    if(IsNumeric($(this).text())){
				    var val_prec=$(this).attr("precision");

				    if(val_prec){
				        precision=val_prec;
				    }
				    var number=parseFloat($(this).text());
				    number=number.toFixed(precision)
				    $(this).text(lisibilite_nombre(number));
				    if($(this).text()=="NaN"){
					$(this).empty();
				    }
			    }
			   else{
			    	$(this).css({'color':'red'});
		   	   }
		      }
                });

		
		
//------------------------------------------------------- End Format type tags-----------------------------------------//
	function get_case(elem){
	       var text=$(elem).text().replace(/^\s*|\s*$/,'');
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
		   var back_h=parseInt(h)+7;
		   var f_back_w=w/4;
		   var f_back_h=parseInt(h)+7;
		   $(elem).find(".input_char_slash td").css({'width':w+'px','height':h+'px','background-size':back_w+'px '+back_h+'px'});
		   $(elem).find(".input_char_slash td:first-child").css({'background-size':f_back_w+'px '+f_back_h+'px'});
	       }
	 }
	 $(".zone_case").each(function( index ) {
	       var text=$(this).text().replace(/^\s*|\s*$/,'');
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
		 /* if(i<text.length){
		     show_text+=text[i];
		  }*/
		  
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
		   var back_h=parseInt(h)+7;
		   var f_back_w=w/4;
		   var f_back_h=parseInt(h)+7;
		  
		   $(this).find(".input_char_slash td").css({'width':w+'px','height':h+'px','background-size':back_w+'px '+back_h+'px'});
		   
		   $(this).find(".input_char_slash td:eq(0)").css({'background-size':f_back_w+'px '+f_back_h+'px','width':'5px'});
	       }
	 });
	 
	 $(".zone_date").each(function( index ) {
	    var date_val=$(this).text().replace(/^\s*|\s*$/,'');
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
	       $(this).css('box-shadow','3px 3px 0px #888888');
	    }
	    if(check_val=="True" || check_val=="true" || check_val=="1" || check_val=="yes" || check_val=="x" || check_val=="X"){
	       $(this).text("x");
	    }else{
	       $(this).empty();
	    }
	 });
}
function page_format(format){
	
	var link = document.createElement('link');
	link.setAttribute('rel', 'stylesheet');
	link.setAttribute('type', 'text/css');
	if(format=="landscape"){
		link.setAttribute('href', '../inclu/style_landscape.css');
	}else{
		link.setAttribute('href', '../inclu/style_portrait.css');
	}
	link.setAttribute('media', 'all');
	
	document.getElementsByTagName('head')[0].appendChild(link);
}
