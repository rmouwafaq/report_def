function engine_report(template_path_name, target){
	    //Loading html file using Ajax 
	    $.get(template_path_name,function(data){
			
			content_html=$('<div>'+data+'</div>');
			content_html.find("meta").remove();

			$("#viewer").html(content_html.html());	
			 
			
		
	      }).then(function(){
		//get invisible data in page_footer and put in footer of table in section details
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
		});

	
	
   
	
}

//lisibilite of nombre ex: lisibilite_nombre(12365555.21) => '12 365 555.21'
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
// format and parsing value of tags in deffirent types(integer,double...)
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
			    $(this).text(lisibilite_nombre(number));
			    //$(this).text(number);
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
