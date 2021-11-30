// Opens collapse menu for this page
$("#admin").collapse("show");

$('[data-onload]').each(function() {
  eval($(this).data('onload'));
});

$(function() {
  $('[data-toggle="tooltip"]').tooltip()
});

$('.glyphicon-calendar').click(function() {  // gets the calender glyphicon
   $(".datepicker").focus();
 });

let date = new Date();
date.setDate(date.getDate());
$(".form-control").datepicker({
});

function getDate(obj, termCode) {
  /* this function makes a dictionary with term code being the keys, and the dates being the values
  then this will trigger the ajax call and send the dictionary to termManagement.py */
  let termStart = obj.value; // You need to get the value of this object otherwise it will show "object Object"
  let termID = obj.id.split("_")[1] // This is how we format the term code
  let dateType = obj.id.split("_")[0] // This variable stores whether the value is a start date or an end date
  let tabledataDict = {};
  let id = "#" + String(obj.id)
  if (obj.value === "") {
    $(id).css('border', '1px solid red')
    $("#flash_container").html('<div class="alert alert-danger" role="alert" id="flasher">Empty date fields are invalid. The previous date has not been deleted.</div>');
    $("#flasher").delay(5000).fadeOut();
  } else {
    $(id).css('border', '')
    tabledataDict[dateType] = obj.value;
    tabledataDict["termCode"] = termID;
    data = JSON.stringify(tabledataDict); // need to do this in order for the python to recognize it
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
          termChanged = response['changedTerm']
          newDate = response['newDate']
          $("#flash_container").html('<div class="alert alert-'+ category +'" role="alert" id="flasher">The '+ dateChanged +' for '+ termChanged +' was changed to '+ newDate +'</div>');
          $("#flasher").delay(5000).fadeOut();
        }
      });
  }
}

function updateStart(obj, termCode) {
  /* This function disables any dates that come after the selected end date */
  let newEnd = new Date(obj.value)
  let dayNewEnd = newEnd.getDate() - 1;
  let monthNewEnd = newEnd.getMonth();
  let yearNewEnd = newEnd.getFullYear();
  $('#start_' + termCode).datepicker({maxDate: new Date(yearNewEnd, monthNewEnd, dayNewEnd)});
  $('#start_' + termCode).datepicker( "option", "maxDate", new Date(yearNewEnd, monthNewEnd, dayNewEnd));
  $('#primaryCutOff_' + termCode).datepicker({maxDate: new Date(yearNewEnd, monthNewEnd, dayNewEnd)});
  $('#primaryCutOff_' + termCode).datepicker( "option", "maxDate", new Date(yearNewEnd, monthNewEnd, dayNewEnd));
  $('#adjustmentCutOff_' + termCode).datepicker({maxDate: new Date(yearNewEnd, monthNewEnd, dayNewEnd)});
  $('#adjustmentCutOff_' + termCode).datepicker( "option", "maxDate", new Date(yearNewEnd, monthNewEnd, dayNewEnd));

}

function updateEnd(obj, termCode) {
  /* This function disables any dates that come after the selected start date */
  let newStart = new Date(obj.value)
  let dayNewStart = newStart.getDate() + 1;
  let monthNewStart = newStart.getMonth();
  let yearNewStart = newStart.getFullYear();
  $('#end_' + termCode).datepicker({minDate: new Date(yearNewStart, monthNewStart, dayNewStart)});
  $("#end_" + termCode).datepicker( "option", "minDate", new Date(yearNewStart, monthNewStart, dayNewStart));
  $('#primaryCutOff_' + termCode).datepicker({minDate: new Date(yearNewStart, monthNewStart, dayNewStart)});
  $("#primaryCutOff_" + termCode).datepicker( "option", "minDate", new Date(yearNewStart, monthNewStart, dayNewStart));
  $('#adjustmentCutOff_' + termCode).datepicker({minDate: new Date(yearNewStart, monthNewStart, dayNewStart)});
  $("#adjustmentCutOff_" + termCode).datepicker( "option", "minDate", new Date(yearNewStart, monthNewStart, dayNewStart));
}

function termStatus(term) {
  /* this function changes the buttons from close and open whenever they are clicked */
  let startID = $("#start_" + term); // This is how we get the unique ID, term is the term code
  let endID = $("#end_" + term);
  let primaryCutOffID = $("#primaryCutOff_" + term);
  let termBtnID = $("#term_btn_" + term);
  let inactiveBtnID = $("#inactive_btn_" + term);
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
        } else {
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
