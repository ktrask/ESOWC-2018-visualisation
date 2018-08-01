function point_it(event){
	pos_x = event.offsetX?(event.offsetX):event.pageX-document.getElementById("pointer_div").offsetLeft;
	pos_y = event.offsetY?(event.offsetY):event.pageY-document.getElementById("pointer_div").offsetTop;
	//document.getElementById("cross").style.left = (pos_x-1) ;
	//document.getElementById("cross").style.top = (pos_y-15) ;
	//document.getElementById("cross").style.visibility = "visible" ;
	//document.pointform.form_x.value = pos_x;
	//document.pointform.form_y.value = pos_y;
  printData(document.pointform, pos_x, pos_y);
}

function printData(destElem, pos_x, pos_y) {
  //$(destElem).html('<img src="{{ url_for('static', filename='loading.gif') }}">');
  $.post('/getInformation', {
                x: pos_x,
                y: pos_y
  }).done(function(response) {
    //document.pointform.form_x.value = response['longitude'];
    $('#popoverdiv').text("Longitude: ".concat(Math.round(response['longitude']* 100) / 100,
      "\nLatitude: ", Math.round(response['latitude']*100)/100));
    $('#popoverdiv').css('visibility', "visible");
    //$('#popoverdiv').form_x.value = response['longitude'];
    //document.pointform.form_y.value = response['latitude'];
    //    $(destElem).text(response['longitude'])
  }).fail(function() {
    $(destElem).text("{{ _('Error: Could not contact server.') }}");
  });
}

$(document).ready(function(){
    $('[data-toggle="popover"]').popover();   
});
