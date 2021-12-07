$(document).ready(function() {
  $( "#dateTimePicker1, #dateTimePicker2").datepicker();
  fillHoursPerWeek();
  jobPositionDisable();
  preFilledDate($("#Term").data("termcode"));
  fetchPositions();
 });

 $("#calendarIcon1").click(function() {
     $("#dateTimePicker1").datepicker('show') // Shows the start date datepicker when glyphicon is clicked
 });

 $("#calendarIcon2").click(function() {
     $("#dateTimePicker2").datepicker('show') // Shows the end date datepicker when glyphicon is clicked
 });

$("#contractHoursDiv").hide();
$("#weeklyHoursDiv").hide();
//adds a contstraint that does not allow user to set date before today's date
let date = new Date();
date.setDate(date.getDate());
$("#datetimepicker0").datepicker({
  minDate: date
});
$("#datetimepicker0").datepicker("setDate", "date");

$(".glyphicon-calendar").click(function() {
    $("#datetimepicker0").focus();
});

function jobPositionDisable() {
  let isBreak = $("#termBreak").data("termbreak");
  if (isBreak) {
    $("#jobType").prop("disabled", true);
    $("#jobType").val("Secondary");
    $("#contractHoursDiv").show();
    $("#weeklyHours").val("");
  } else {
    $("#weeklyHoursDiv").show();
    $("#contractHours").val("");
  }
}

function fillHoursPerWeek() { // prefill hours per week select picker
  let defaultValue = $("#oldWeeklyHours").val();
  let selectedHoursPerWeek = $("#weeklyHours");
  let jobType = $("#jobType").val();
  let wls = $("#position option:selected").attr("data-wls");
  if (selectedHoursPerWeek) {
    let list = ["10", "12", "15", "20"];
    if (jobType == "Secondary") {
      list = ["5","10"]
    }
    if (wls >= 5) {
      list = ["15", "20"]
      // Here we need to pop open the modal that says they need atleast 15 hours
    }
    $("#weeklyHours").empty();
    $(list).each(function(i,hours) {
      selectedHoursPerWeek.append($("<option />").text(hours).val(hours));
    });
    if (wls >= 5){
      if (Number(defaultValue) >= 15) {
        $("#weeklyHours").val(defaultValue);
        $("#weeklyHours").selectpicker("render");
        $("#weeklyHours").selectpicker("refresh");
      } else {
        $("#weeklyHours").val('15');
        $("#weeklyHours").selectpicker("render");
        $("#weeklyHours").selectpicker("refresh");
        $("#warningModalTitle").html("Work-Learning-Service Levels (WLS)");
        $("#warningModalText").html("Student with WLS Level 5 or 6 must have at least a 15 hour contract. " +
                                 "These positions require special authorization as specified at " +
                                 "<a href=\"http://catalog.berea.edu/2014-2015/Tools/Work-Learning-Service-Levels-WLS\""+
                                 "target=\"_blank\">The Labor Program Website.</a>");
        $("#warningModalButton").css('display', 'none');
        $("#resetConfirmButton").css('display', 'none');
        $("#warningModal").modal("show");
      }
    } else {
        $("#weeklyHours").val(defaultValue);
        $("#weeklyHours").selectpicker("render");
        $("#weeklyHours").selectpicker("refresh");
    }
    $("#weeklyHours").selectpicker("refresh");
  }
}

let effectiveDate = $("#datetimepicker0").datepicker("getDate");
let finalDict = {};

function checkWLS20() {
  totalhours = $("#totalHours").val();
  weeklyHours = $("#weeklyHours").val();
  if (weeklyHours == "20") {
    $("#OverloadModal").modal("show");
    $("#overloadModalButton").attr("data-target", "") // prevent a Primary Modal from showing up
  } else if (Number(totalhours) + Number(weeklyHours) > 15) {
    $("#OverloadModal").modal("show");
    $("#overloadModalButton").attr("data-target", "") // prevent a Primary Modal from showing up
  }
}

function checkSupervisor() {
  let oldSupervisor = $('#prefillsupervisor').val();
  let supervisor = $('#supervisor').val()
  let position = $('#position').val()
  let oldPostition = $('#prefillposition').val()
  let weeklyHours = $('#weeklyHours').val()
  let oldWeeklyHours = $('#oldWeeklyHours').val()
  let contractHours = $('#contractHours').val()
  let oldContractHours = $('#oldContractHours').val()

  if (supervisor != oldSupervisor) {
    $('#position').val(oldPostition);
    $("#position").prop('disabled', true);
    $('#position').selectpicker('refresh');
    $('#weeklyHours').val(oldWeeklyHours);
    $("#weeklyHours").prop('disabled', true);
    $('#weeklyHours').selectpicker('refresh');
    $('#contractHours').val(oldContractHours);
    $("#contractHours").prop('disabled', true);
    $('#contractHours').selectpicker('refresh');
    $("#department").prop('disabled', true);
    $('#department').selectpicker('refresh');
    category = "info"
    msg = "Changes to Department, Position, and Hours are unavailable when Supervisor is changed. (Select Original Supervisor to change Department, Position or Hours)";
    $("#flash_container").html('<div class="alert alert-'+ category +'" role="alert" id="flasher">'+msg+'</div>')
    $("#flasher").delay(3000).fadeOut()
  } else {
    $("#position").prop('disabled', false)
    $('#position').selectpicker('refresh');
    $("#weeklyHours").prop('disabled', false);
    $('#weeklyHours').selectpicker('refresh');
    $("#contractHours").prop('disabled', false);
    $('#contractHours').selectpicker('refresh');
    $("#department").prop('disabled', false);
    $('#department').selectpicker('refresh');
  }
}

function checkForChange() {
  let oldSupervisor = $("#prefillsupervisor").val();
  let newSupervisor = $("#supervisor").val();
  let oldPostition = $("#prefillposition").val();
  let newPosition = $("#position").val();
  let date = $("#datetimepicker0").val();
  let newNotes = $("#supervisorNotes").val();
  let oldContractHours = $("#oldContractHours").val();
  let newContractHours = $("#contractHours").val();
  let oldWeeklyHours = $("#oldWeeklyHours").val();
  let newWeeklyHours = $("#weeklyHours").val();
  let oldStartDate = $("#oldStartDate").val();
  let newStartDate = $("#dateTimePicker1").val();
  let oldEndDate = $("#oldEndDate").val();
  let newEndDate = $("#dateTimePicker2").val();
  let oldDepartment = $('#prefilldepartment').val();
  let newDepartment = $('#department').val();

  if (oldSupervisor != newSupervisor) {
    finalDict["supervisor"] = {"oldValue": oldSupervisor, "newValue": newSupervisor, "date": date}
  }
  if (oldPostition != newPosition) {
    finalDict["position"] = {"oldValue": oldPostition, "newValue": newPosition, "date": date}
  }
  if (newNotes) {
    finalDict["supervisorNotes"] = {"newValue": newNotes, "date": date}
  }
  if (oldContractHours != newContractHours && newWeeklyHours == "") {
    finalDict["contractHours"] = {"oldValue": oldContractHours, "newValue": newContractHours, "date": date}
  }
  if (oldWeeklyHours != newWeeklyHours && newContractHours == "") {
    finalDict["weeklyHours"] = {"oldValue": oldWeeklyHours, "newValue": newWeeklyHours, "date": date}
  }
  if (oldStartDate != newStartDate) {
    finalDict["startDate"] = {"oldValue": oldStartDate, "newValue": newStartDate, "date": date}
  }
  if (oldEndDate != newEndDate) {
    finalDict["endDate"] = {"oldValue": oldEndDate, "newValue": newEndDate, "date": date}
  }
  if (oldDepartment != newDepartment) {
    finalDict["department"] = {"oldValue": oldDepartment, "newValue": newDepartment, "date": date}
  }

  if (JSON.stringify(finalDict) == "{}" || (Object.keys(finalDict).length == 1 && Object.keys(finalDict) == "supervisorNotes")) {
    $("#NochangeModal").modal("show");
  } else if (newNotes == '') {
    category = "danger"
    msg = "Please make sure Notes is filled out.";
    $("#flash_container").html('<div class="alert alert-'+ category +'" role="alert" id="flasher">'+msg+'</div>')
    $("#flasher").delay(3000).fadeOut()
  } else if (JSON.stringify(finalDict) !== "{}") {
    $("#submitModal").modal("show");
    return finalDict
  }
}

function buttonListener(laborStatusKey) {
  event.preventDefault();
  $('#modal').html('Processing');
  $('#modal').prop('disabled', 'True');
  $('#adjustmentClose').prop('disabled', 'True');
  $.ajax({
    url: "/alterLSF/submitAlteredLSF/" + laborStatusKey,
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(finalDict),
    success: function(response) {
      window.location.href = document.referrer;
    }
  })
}

function preFilledDate(obj) { // get term start date and end date
  $.ajax({
    url: "/alterLSF/getDate/" + obj,
    dataType: "json",
    success: function (response){
       fillDates(response);
    }
  });
}

function fillDates(response) { // prefill term start and term end
  for (let key in response) {
    let start = response[key]["Start Date"];
    let end = response[key]["End Date"];
    let primaryCutOff = response[key]["Primary Cut Off"];
    // disabling primary position if cut off date is before today's date
    let today = new Date();
    let date = ("0"+(today.getMonth()+1)).slice(-2)+"/"+("0"+today.getDate()).slice(-2)+"/"+today.getFullYear();

    // Start Date
    let startd = new Date(start);
    let dayStart1 = startd.getDate();
    let monthStart1 = startd.getMonth();
    let yearStart = startd.getFullYear();
    // End Date
    let endd = new Date(end);
    let dayEnd1 = endd.getDate();
    let monthEnd1 = endd.getMonth();
    let yearEnd = endd.getFullYear();
    // Pre-populate values
    $("#dateTimePicker1").val(start);
    $("#dateTimePicker2").val(end);
    // set the minimum and maximum Date for Term Start Date
    $("#dateTimePicker1").datepicker({minDate: new Date(yearStart, monthStart1, dayStart1)});
    $("#dateTimePicker1").datepicker({maxDate: new Date(yearEnd, monthEnd1, dayEnd1)});
    $("#dateTimePicker1").datepicker("option", "minDate", new Date(yearStart, monthStart1, dayStart1));
    $("#dateTimePicker1").datepicker("option", "maxDate", new Date(yearEnd, monthEnd1, dayEnd1));
    // set the minimum and maximum Date for Term End Date
    $("#dateTimePicker2").datepicker({maxDate: new Date(yearEnd, monthEnd1, dayEnd1)});
    $("#dateTimePicker2").datepicker({minDate: new Date(yearStart, monthStart1, dayStart1)});
    $("#dateTimePicker2").datepicker("option", "maxDate", new Date(yearEnd, monthEnd1, dayEnd1));
    $("#dateTimePicker2").datepicker("option", "minDate", new Date(yearStart, monthStart1, dayStart1));
  }
}

function updateDate(obj) { // updates max and min dates of the datepickers as the other datepicker changes
  let dateToChange = new Date($(obj).val());
  let newMonth = dateToChange.getMonth();
  let newYear = dateToChange.getFullYear();
  if (obj.id == "dateTimePicker2") {
    let newDay = dateToChange.getDate() - 1;
    $("#dateTimePicker1").datepicker({maxDate: new Date(newYear, newMonth, newDay)});
    $("#dateTimePicker1").datepicker("option", "maxDate", new Date(newYear, newMonth, newDay));
  }
  if (obj.id == "dateTimePicker1") {
    let newDay = dateToChange.getDate() + 1;
    $("#dateTimePicker2").datepicker({minDate: new Date(newYear, newMonth, newDay)});
    $("#dateTimePicker2").datepicker( "option", "minDate", new Date(newYear, newMonth, newDay));
  }
}

function fetchPositions() {
  departmentOrg = $('#department').val();
  departmentAccount = $("#department option:selected").attr("data-account");
  positionsSelectpicker = $("#position");
  $.ajax({
    url: `/alterLSF/fetchPositions/${departmentOrg}/${departmentAccount}`,
    dataType: "json",
    success: function(positions) {
      for (var position in positions) {
        positionsSelectpicker.append(
          $("<option />")
             .attr("data-content", `${positions[position].POSN_TITLE} (${positions[position].WLS})`)
             .attr("value", positions[position].POSN_CODE)
             .attr("data-wls",positions[position].WLS)
        );
      }
     $("#position").selectpicker("refresh");
     $("#position").selectpicker("refresh");
    }
  });
}

$('#department').on('change',function() {
  $("#position").empty();
  $("#position").selectpicker("refresh");
  fetchPositions();
});
