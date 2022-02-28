// Opens collapse menu for this page
$("#admin").collapse("show");

$('[data-onload]').each(function(){
  eval($(this).data('onload'));
});

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});

$('.glyphicon-calendar').click(function() {  // gets the calender glyphicon
   $(".datepicker").focus();
 });

var date = new Date();
date.setDate(date.getDate());
$(".form-control").datepicker({
});

function getDate(obj, termCode) {
  /* this function makes a dictionary with term code being the keys, and the dates being the values
  then this will trigger the ajax call and send the dictionary to termManagement.py */
  var termStart = obj.value; // You need to get the value of this object otherwise it will show "object Object"
  var termID = obj.id.split("_")[1] // This is how we format the term code
  var dateType = obj.id.split("_")[0] // This variable stores whether the value is a start date or an end date
  var tabledata_dict = {};
  var id = "#" + String(obj.id)
  if (obj.value === "") {
    $(id).css('border', '1px solid red')
    $("#flash_container").html('<div class="alert alert-danger" role="alert" id="flasher">Empty date fields are invalid. The previous date has not been deleted.</div>');
    $("#flasher").delay(5000).fadeOut();
  } else {
    $(id).css('border', '')
    tabledata_dict[dateType] = obj.value;
    tabledata_dict["termCode"] = termID;
    data = JSON.stringify(tabledata_dict); // need to do this in order for the python to recognize it
      $.ajax({
        type: "POST",
        url: "/termManagement/setDate/",
        datatype: "json",
        data: data,
        contentType: 'application/json',
        success: function(response){
          stateBtnValue = $("#term_btn_" + termCode).val();
          start = $("#start_" + termCode).val();
          end = $("#end_" +termCode).val();
          primaryCutOff = $("#primaryCutOff_" + termCode).val();
          adjustmentCutOff = $("#adjustmentCutOff_" + termCode).val();

          if (start != "" && end != "" && primaryCutOff != "" && adjustmentCutOff != "") {
            $('#term_btn_' + termCode).prop('disabled', false)
          }
          category = "info"
          dateChanged = response['dateChanged']
          termchanged = response['changedTerm']
          newDate = response['newDate']
          $("#flash_container").html('<div class="alert alert-'+ category +'" role="alert" id="flasher">The '+ dateChanged +' for '+ termchanged +' was changed to '+ newDate +'</div>');
          $("#flasher").delay(5000).fadeOut();
        }

      });
  }
}

function updateStart(obj, termCode){
  /* This function disables any dates that come after the selected end date */
  var newEnd = new Date(obj.value)
  var dayNewEnd = newEnd.getDate() - 1;
  var monthNewEnd = newEnd.getMonth();
  var yearNewEnd = newEnd.getFullYear();
  $('#start_' + termCode).datepicker({maxDate: new Date(yearNewEnd, monthNewEnd, dayNewEnd)});
  $('#start_' + termCode).datepicker( "option", "maxDate", new Date(yearNewEnd, monthNewEnd, dayNewEnd));
  $('#primaryCutOff_' + termCode).datepicker({maxDate: new Date(yearNewEnd, monthNewEnd, dayNewEnd)});
  $('#primaryCutOff_' + termCode).datepicker( "option", "maxDate", new Date(yearNewEnd, monthNewEnd, dayNewEnd));
  $('#adjustmentCutOff_' + termCode).datepicker({maxDate: new Date(yearNewEnd, monthNewEnd, dayNewEnd)});
  $('#adjustmentCutOff_' + termCode).datepicker( "option", "maxDate", new Date(yearNewEnd, monthNewEnd, dayNewEnd));

}

function updateEnd(obj, termCode){
  /* This function disables any dates that come after the selected start date */
  var newStart = new Date(obj.value)
  var dayNewStart = newStart.getDate() + 1;
  var monthNewStart = newStart.getMonth();
  var yearNewStart = newStart.getFullYear();
  $('#end_' + termCode).datepicker({minDate: new Date(yearNewStart, monthNewStart, dayNewStart)});
  $("#end_" + termCode).datepicker( "option", "minDate", new Date(yearNewStart, monthNewStart, dayNewStart));
  $('#primaryCutOff_' + termCode).datepicker({minDate: new Date(yearNewStart, monthNewStart, dayNewStart)});
  $("#primaryCutOff_" + termCode).datepicker( "option", "minDate", new Date(yearNewStart, monthNewStart, dayNewStart));
  $('#adjustmentCutOff_' + termCode).datepicker({minDate: new Date(yearNewStart, monthNewStart, dayNewStart)});
  $("#adjustmentCutOff_" + termCode).datepicker( "option", "minDate", new Date(yearNewStart, monthNewStart, dayNewStart));
}

function termStatus(term) {
  /* this function changes the buttons from close and open whenever they are clicked */
  var startID = $("#start_" + term); // This is how we get the unique ID, term is the term code
  var endID = $("#end_" + term);
  var primaryCutOffID = $("#primaryCutOff_" + term);
  var termBtnID = $("#term_btn_" + term);
  var inactiveBtnID = $("#inactive_btn_" + term);
    $.ajax({
      method: "POST",
      url: "/termManagement/manageStatus ",
      dataType: "json",
      contentType: "application/json",
      data: JSON.stringify({"termBtn": term}),
      processData: false,
      success: function(response) {
        //category = "info"
        if($(termBtnID).hasClass("btn-success")) {
          $(termBtnID).removeClass("btn-success");
          $(termBtnID).addClass("btn-danger");
          $(termBtnID).text("Closed");
          category = "danger";
          state = "'Closed'.";
          }
        else {
          $(termBtnID).removeClass("btn-danger");
          $(termBtnID).addClass("btn-success");
          $(termBtnID).text("Open");
          category = "success";
          state = "'Open'.";
        }
        term = response['termChanged']
        $("#flash_container").html('<div class="alert alert-'+ category +'" role="alert" id="flasher">The state for '+ term +' is set to '+ state +'</div>');
        $("#flasher").delay(5000).fadeOut();
     }
  })
};

function toggleEval(term, isMidyear) {
  if (isMidyear) {
      var evalBtnID = $("#midyear_eval_btn_" + term);
  } else {
    var evalBtnID = $("#eval_btn_" + term);
  }
  $.ajax({
    method: "POST",
    url: "/termManagement/manageEval",
    dataType: "json",
    contentType: "application/json",
    data: JSON.stringify({"evalBtn": term, "isMidyear": isMidyear}),
    processData: false,
    success: function(response) {
      if($(evalBtnID).hasClass("btn-success")) {
        $(evalBtnID).removeClass("btn-success");
        $(evalBtnID).addClass("btn-danger");
        $(evalBtnID).text("Closed");
        category = "danger";
        state = "'Closed'.";
        }
      else {
        $(evalBtnID).removeClass("btn-danger");
        $(evalBtnID).addClass("btn-success");
        $(evalBtnID).text("Open");
        category = "success";
        state = "'Open'.";
      }
      term = response['termChanged']
      message = "The "+ (isMidyear ? "midyear ":"final ") +"evaluations for "+ term +' is set to '+ state
      $("#flash_container").html('<div class="alert alert-'+ category +'" role="alert" id="flasher">' + message + '</div>');
      $("#flasher").delay(5000).fadeOut();
    }
  });
}
