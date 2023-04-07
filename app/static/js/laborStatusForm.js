var globalArrayOfStudents = [];
var display_failed = [];
var laborStatusFormNote = null;

$(document).ready(function(){
  intializeDataTable()
  if($("#selectedDepartment").val()){ // prepopulates position on redirect from rehire button and checks whether department is in compliance.
    checkCompliance($("#selectedDepartment"));
    getDepartment($("#selectedDepartment"));
  }
  if($("#jobType").val()){ // fills hours per week selectpicker with correct information from laborstatusform. This is triggered on redirect from form history.
    var value = $("#selectedHoursPerWeek").val();
    $("#selectedHoursPerWeek").val(value);
    fillHoursPerWeek("fillhours");
  }
  var cookies = document.cookie;
  if (cookies){
    parsedArrayOfStudentCookies = JSON.parse(cookies);
    document.cookie = parsedArrayOfStudentCookies + ";max-age=28800;";
    for (i in parsedArrayOfStudentCookies) {
      createAndFillTable(parsedArrayOfStudentCookies[i]);
    }
    $("#selectedTerm option[value=" + parsedArrayOfStudentCookies[0].stuTermCode + "]").attr('selected', 'selected');
    $("#selectedSupervisor option[value=" + parsedArrayOfStudentCookies[0].stuSupervisorID + "]").attr('selected', 'selected');
    $("#selectedDepartment option[value=\"" + parsedArrayOfStudentCookies[0].stuDepartmentORG + "\"]").attr('selected', 'selected');
    getDepartment($("#selectedDepartment"));
    preFilledDate($("#selectedTerm"));
    showAccessLevel($("#selectedTerm"));
    disableTermSupervisorDept();
  }
});

$("#laborStatusForm").submit(function(event) {
  event.preventDefault();
});

$("#calendarIcon1").click(function() {
    $("#dateTimePicker1").datepicker('show') // Shows the start date datepicker when glyphicon is clicked
});

$("#calendarIcon2").click(function() {
    $("#dateTimePicker2").datepicker('show') // Shows the end date datepicker when glyphicon is clicked
});

$(document).on("keyup", "input[name=contractHours]", function () { // sets contract hours minimum value
   var _this = $(this);
   var min = parseInt(_this.attr("min")) || 1; // if min attribute is not defined, 1 is default
   var val = parseInt(_this.val()) || (min - 1); // if input char is not a number the value will be (min - 1) so first condition will be true
   if(val < min) {
       _this.val( min );
     }
});

$("#jobType").change(function(){ // Pops up a modal for Seconday Postion
  //this is just getting the value that is selected
  var jobType = $(this).val();
  if (jobType == "Secondary") {
      $("#warningModal").modal("show");
      $("#warningModalTitle").html("Warning"); //Maybe change the wording here.
      $("#warningModalText").html("The labor student and the supervisor of this secondary position should obtain permission from the primary supervisor before submitting this labor status form.");
      }
  });

function checkIfFreshman() {
  var jobType = $("#jobType").val();
  var wls = $("#position :selected").attr("data-wls")
  var classLevel = $("#student :selected").attr("data-stuCL");
  if (classLevel == "Freshman" && jobType == "Secondary") {
    laborStatusFormNote = "Warning! This student has freshman classification with either a secondary position or a primary position with a WLS greater than 1. Make sure they meet the requirements for these positions.";
  }
  if (classLevel == "Freshman" && wls > 1) {
    laborStatusFormNote = "Warning! This student has freshman classification with either a secondary position or a primary position with a WLS greater than 1. Make sure they meet the requirements for these positions.";
  }
  else {
    laborStatusFormNote = null;
  }
  searchDataToPrepareToCheckPrimaryPosition();
}

function disableTermSupervisorDept() {
  // disables term, supervisor and department select pickers when add student button is clicked
    $("#selectedTerm").prop("disabled", "disabled");
    $("#termInfo").show();
    $("#selectedTerm").selectpicker("refresh");
    $("#selectedSupervisor").prop("disabled", "disabled");
    $("#supervisorInfo").show();
    $("#selectedSupervisor").selectpicker("refresh");
    $("#selectedDepartment").prop("disabled", "disabled");
    $("#departmentInfo").show();
    $("#selectedDepartment").selectpicker("refresh");
}

function preFilledDate(obj){ // get term start date and end date
  var termCode = $(obj).val();
  $.ajax({
    url: "/laborstatusform/getDate/" + termCode,
    dataType: "json",
    success: function (response){
       fillDates(response);
    }
  });
}

function fillDates(response) { // prefill term start and term end
  $("#primary-cutoff-warning").hide();
  $("#break-cutoff-warning").hide();
  $("#primary-cutoff-date").text("");
  $("#addMoreStudent").show();

  $("#selectedTerm").on("change", function(){
    $("#jobType").val('');
  });
  for (var key in response){
    var start = response[key]["Start Date"];
    var end = response[key]["End Date"];
    var primaryCutOff = response[key]["Primary Cut Off"];
    // disabling primary position if cut off date is before today's date
    var today = new Date();
    var date = ("0"+(today.getMonth()+1)).slice(-2)+"/"+("0"+today.getDate()).slice(-2)+"/"+today.getFullYear();
    var isBreak = response[key]["isBreak"];
    var isSummer = response[key]["isSummer"];
    if (primaryCutOff){
      if (isBreak){
        if (Date.parse(date) > Date.parse(primaryCutOff)){
        msgFlash("The deadline to add break positions has ended.", "fail");
        $("#break-cutoff-warning").show();
        $("#break-cutoff-date").text(primaryCutOff);
        $("#addMoreStudent").hide();
        }
      }
      else{
        if (Date.parse(date) > Date.parse(primaryCutOff)){
          $("#jobType option[value='Primary']").attr("disabled", true );
          $('.selectpicker').selectpicker('refresh');
          msgFlash("Disabling primary position because cut off date is before today's date", "fail");
          $("#primary-cutoff-warning").show();
          $("#primary-cutoff-date").text(primaryCutOff);
        }
        else{
          $("#jobType option[value='Primary']").attr("disabled", false );
          $('.selectpicker').selectpicker('refresh');
        }
      }

    }
    // Start Date
    var startd = new Date(start);
    var dayStart1 = startd.getDate();
    var monthStart1 = startd.getMonth();
    var yearStart = startd.getFullYear();
    // End Date
    var endd = new Date(end);
    var dayEnd1 = endd.getDate();
    var monthEnd1 = endd.getMonth();
    var yearEnd = endd.getFullYear();
    // Pre-populate values
    $("#dateTimePicker1").val(start);
    $("#dateTimePicker2").val(end);
    $("#dateTimePicker1").datepicker("option", "minDate", new Date(yearStart, monthStart1, dayStart1));
    $("#dateTimePicker1").datepicker("option", "maxDate", new Date(yearEnd, monthEnd1, dayEnd1));
    $("#dateTimePicker2").datepicker("option", "maxDate", new Date(yearEnd, monthEnd1, dayEnd1));
    $("#dateTimePicker2").datepicker("option", "minDate", new Date(yearStart, monthStart1, dayStart1));
    $("#dateTimePicker1").datepicker({
      beforeShowDay: function(d) {

        if(d.getTime() < startd.getTime()){
          return [false, 'datePicker', 'Before Term Start'];
        }
        else if (d.getTime() > endd.getTime()) {
          return [false, 'datePicker', 'After Term End'];
        }else{
            return [true, '', 'Available'];
        }
    },
  });
    $("#dateTimePicker2").datepicker({
    beforeShowDay: function(d) {

        if(d.getTime() > endd.getTime()){
          return [false, 'datePicker', 'After Term End'];
        }
        else if (d.getTime() < startd.getTime()) {
          return [false, 'datePicker', 'Before Term Start'];
        }else{
            return [true, '', 'Available'];
        }
    },
    });
  }
}

function updateDate(obj) { // updates max and min dates of the datepickers as the other datepicker changes
  var dateToChange = new Date($(obj).val());
  var newMonth = dateToChange.getMonth();
  var newYear = dateToChange.getFullYear();
  if(obj.id == "dateTimePicker2"){
    var newDay = dateToChange.getDate() - 1;
    $("#dateTimePicker1").datepicker({maxDate: new Date(newYear, newMonth, newDay)});
    $("#dateTimePicker1").datepicker("option", "maxDate", new Date(newYear, newMonth, newDay));
  }
  if(obj.id == "dateTimePicker1"){
    var newDay = dateToChange.getDate() + 1;
    $("#dateTimePicker2").datepicker({minDate: new Date(newYear, newMonth, newDay)});
    $("#dateTimePicker2").datepicker( "option", "minDate", new Date(newYear, newMonth, newDay));
  }
}

function getDepartment(object, stopSelectRefresh="") { // get department from select picker
   var departmentOrg = $(object).val();
   var departmentAcct = $(object).find('option:selected').attr('value-account');
   var url = "/laborstatusform/getPositions/" + departmentOrg + "/" + departmentAcct;
       $.ajax({
         url: url,
         dataType: "json",
         success: function (response){

           fillPositions(response, stopSelectRefresh);
          }
        });
  }

 function fillPositions(response, stopSelectRefresh="") { // prefill Position select picker with the positions of the selected department
   var selectedPositions = $("#position");
   $("#position").empty();
   for (var key in response) {
     selectedPositions.append(
       $("<option />")
          .attr("data-content", "<span>" + response[key].position + " " + "(" + response[key].WLS+ ")"
          + "</span>" + "<small class='text-muted'>" + " " + "(" + response[key].positionCode + ")" + "</small>")
          .attr("id", key)
          .attr("value", response[key].position)
          .attr("data-wls", response[key].WLS)
     );

   }
   if (stopSelectRefresh== "") {
     $(".selectpicker").selectpicker("refresh");
   }
   else {
     value = $("#position").val();
     $("#position").val(value);
   }
 }

 // Pops up a modal for WLS 5, 6 or more
 $("#position").change(function(){
   //this is just getting the value that is selected
   var wls = $("#position").find("option:selected").attr("data-wls");
   var isBreak = $("#selectedTerm").find("option:selected").data("termbreak");
   //We only want to show the modal if the selected term is 'Spring', 'Fall', or 'AY'
   if (!isBreak) {
     if (wls >= 5) {
       $("#warningModalTitle").html("Work-Learning-Service Levels (WLS)");
       $("#warningModalText").html("Student with WLS Level 5 or 6 must have at least a 15 hour contract. " +
                                "These positions require special authorization as specified at " +
                                "<a href=\"http://catalog.berea.edu/2014-2015/Tools/Work-Learning-Service-Levels-WLS\""+
                                "target=\"_blank\">The Labor Program Website.</a>");
       $("#warningModal").modal("show");
   }
 }
});

 function fillHoursPerWeek(fillhours=""){ // prefill hours per week select picker
  var selectedHoursPerWeek = $("#selectedHoursPerWeek");
  var jobType = $("#jobType").val();
  var position = $("#position").val();

  if (selectedHoursPerWeek){
    $("#selectedHoursPerWeek").empty();
    if (fillhours == ""){
      $(".selectpicker").selectpicker("refresh");
    }
    var list = ["10", "12", "15", "20"];
    if (position.toLowerCase() == "no labor"){
      list = ["0"];
    }
    else if (jobType == "Secondary"){
       list = ["5", "10"];
    }
    $(list).each(function(i,hours) {
      selectedHoursPerWeek.append($("<option />").text(hours));
    });
  }
    if (fillhours == ""){
      $(".selectpicker").selectpicker("refresh");
    }
  }

// checks if wls is greater than 5
function checkWLS() {
  var wls = $("#position").find("option:selected").attr("data-wls");
  var hoursPerWeek = $("#selectedHoursPerWeek").val();
  var isBreak = $("#selectedTerm").find("option:selected").data("termbreak");
  //We only want to show the modal if the selected term is 'Spring', 'Fall', or 'AY'
  if (!isBreak) {
    if (wls >= 5 && hoursPerWeek < 15 ) {
      $("#warningModalTitle").html("Insert Rejected");
      $("#warningModalText").html("Student requires at least a 15 hour contract with positions that are WLS 5 or greater.  Please also make sure that job type is not secondary for positions that are WLS 5 or greater.");
      $("#warningModal").modal("show");
      return false;
    }
  }
  else {
    return true;
  }
}

// Check if department is in compliance.
function checkCompliance(obj) {
  $("#dept-compliance-warning").hide();
  $("#departmentClass").removeClass(" has-error")
  var department = $(obj).val();
  var url = "/laborstatusform/getcompliance/" + department;
      $.ajax({
        url: url,
        dataType: "json",
        success: function (response){
          if(response.Department["Department Compliance"] == false){
            $("#warningModal").modal("show");
            $("#warningModalTitle").html("Warning");
            $("#warningModalText").html("The "+ department +" Department is out of compliance. Please contact the Labor Office.");
            $(".disable").prop("disabled", true);
            $("#addMoreStudent").prop("disabled", true);
            $("#selectedTerm").selectpicker("refresh");
            $("#student").selectpicker("refresh");
            $("#position").selectpicker("refresh");
            $("#selectedSupervisor").selectpicker("refresh");
            $("#selectedDepartment").selectpicker("refresh");
            $("#dept-name-compliance").text(department);
            $("#dept-compliance-warning").show();
            $("#departmentClass").addClass(" has-error")
          }
          else{
            $(".disable").prop("disabled", false);
          }
        }
      });
}

// TABLE LABELS
$("#contractHours").hide();
$("#hoursPerWeek").hide();
$("#JobTypes").hide();
$("#plus").hide();
$("#failedTable").hide();


function showAccessLevel(){ // Make Table labels appear
  if ($("#selectedSupervisor").val() && $("#selectedDepartment").val() && $("#selectedTerm").val()){
    var isBreak = $("#selectedTerm").find("option:selected").data("termbreak");
    if (isBreak) { // Summer term or any other break period table labels
      $("#contractHours").show();
      $("#plus").show();
      $("#JobTypes").hide();
      $("#hoursPerWeek").hide();
    }
    else{ // normal semester like Fall or Spring table labels
      $("#hoursPerWeek").show();
      $("#JobTypes").show();
      $("#plus").show();
      $("#contractHours").hide();
    }
  }
}
// TABLE LABELS

// hide review button will show when add student is clicked
$("#reviewButton").hide();
//end

// Table glyphicons
function showNotesModal(glyphicon){// pops up Note Modal when notes glyphicon is clicked
  var rowParent = glyphicon.parentNode.parentNode;
  var table = document.getElementById("mytable").getElementsByTagName("tbody")[0];
  for (var i = 0, row; row = table.rows[i]; i++) {
    if (rowParent === table.rows[i]) {
      $("#modal_text").val(globalArrayOfStudents[i].stuNotes);
      $("#saveButton").attr("onclick","saveNotes(\"" + i +"\")");
      break;
    }
  }
  $("#noteModal").modal("show");
}

function saveNotes(arrayIndex){ // saves notes written in textarea when save button of modal is clicked
  if($("#modal_text").val() != ""){
    globalArrayOfStudents[arrayIndex].stuNotes = $("#modal_text").val();
  }
}

function deleteRow(glyphicon) {
  var rowParent = glyphicon.parentNode.parentNode;
  var table = document.getElementById("mytable").getElementsByTagName("tbody")[0];
  for (var i = 0, row; row = table.rows[i]; i++) {
    if (rowParent === table.rows[i]) {
      $(glyphicon).parents("tr").remove();
      globalArrayOfStudents.splice(i, 1);
      if(globalArrayOfStudents.length > 1){
        document.cookie = JSON.stringify(globalArrayOfStudents) + ";max-age=28800;";
      }
      else {
        parsedArrayOfStudentCookies = document.cookie;
        document.cookie = parsedArrayOfStudentCookies + ";max-age=0;";
      }
      break;
    }
  }
  if (globalArrayOfStudents.length <= 0) {
    $("#selectedTerm").prop("disabled", false);
    $("#selectedTerm").selectpicker("refresh");
    $("#selectedSupervisor").prop("disabled", false);
    $("#selectedSupervisor").selectpicker("refresh");
    $("#selectedDepartment").prop("disabled", false);
    $("#selectedDepartment").selectpicker("refresh");
  }
}
//END of glyphicons

function msgFlash(flash_message, status){
    if (status === "success") {
        category = "success";
        $("#flash_container").prepend("<div class=\"alert alert-"+ category +"\" role=\"alert\" id=\"flasher\">"+flash_message+"</div>");
        $("#flasher").delay(5000).fadeOut();
    }
    else {
        category = "danger";
        $("#flash_container").prepend("<div class=\"alert alert-"+ category +"\" role=\"alert\" id=\"flasher\">"+flash_message+"</div>");
        $("#flasher").delay(5000).fadeOut();
    }

}

// TABLE
function searchDataToPrepareToCheckPrimaryPosition() { // displays table when plus glyphicon is clicked and check if fields are filled out
  var studentDict = createStuDict();
  if (studentDict === false) {
    msgFlash("Please make sure that the Student, Position (WLS), Job Type, and Hours Per Week fields are filled out before submitting.", "fail");
  }
  else if (checkWLS() === false) {
    // checkWLS();
  }
  else  {
    disableTermSupervisorDept();
    checkPrimaryPositionToCreateTheTable(studentDict);
    isOneLaborStatusForm(studentDict);
     }
  }

function createStuDict(){
  var supervisor = $("#selectedSupervisor").find("option:selected").text();
  var supervisorID = $("#selectedSupervisor").find("option:selected").attr("value");
  var department = $("#selectedDepartment").find("option:selected").text();
  var departmentORG = $("#selectedDepartment").find("option:selected").val();
  var departmentAccount = $("#selectedDepartment").find("option:selected").data("account");
  var termCodeSelected = $("#selectedTerm").find("option:selected").val();
  var isBreak = $("#selectedTerm").find("option:selected").data("termbreak")
  var studentName = $("#student option:selected").text();
  if (!studentName){
    return false;
  }
  var positionName = $("#position option:selected").attr("value");
  if (!positionName){
    return false;
  }
  var positionCode = $("#position").find("option:selected").attr("id");
  var wls = $("#position").find("option:selected").attr("data-wls");
  var studentBNumber = $("#student").val();
  var startDate  = $("#dateTimePicker1").datepicker({dateFormat: "dd-mm-yy"}).val();
  var endDate  = $("#dateTimePicker2").datepicker({dateFormat: "dd-mm-yy"}).val();
  if (!isBreak){
    var jobType = $("#jobType");
    var jobTypeName = $("#jobType option:selected").text();
    var hoursPerWeek = $("#selectedHoursPerWeek");
    var hoursPerWeekName = $("#selectedHoursPerWeek :selected").val();
    if (!hoursPerWeekName){
      return false;
      }
    }
  else {
    var jobTypeName = "Secondary";
    var selectedContractHoursName = $("#selectedContractHours").val();
    if (selectedContractHoursName === ""){
        return false;
      }
    }
  var studentDict = {stuName: studentName.trim(),
                    stuBNumber: studentBNumber.trim(),
                    stuPosition: positionName,
                    stuPositionCode: positionCode,
                    stuJobType: jobTypeName,
                    stuWeeklyHours: parseInt(hoursPerWeekName, 10),
                    stuContractHours: parseInt(selectedContractHoursName, 10),
                    stuWLS: wls,
                    stuStartDate: startDate,
                    stuEndDate: endDate,
                    stuTermCode: termCodeSelected,
                    stuNotes: "",
                    stuLaborNotes: laborStatusFormNote,
                    stuSupervisor: supervisor.trim(),
                    stuDepartment: department.trim(),
                    stuDepartmentORG: departmentORG,
                    stuDepartmentAccount: departmentAccount,
                    stuSupervisorID: supervisorID,
                    isItOverloadForm: "False",
                    isTermBreak: isBreak
                    };
    return studentDict;
  }

function checkDuplicate(studentDict) {// checks for duplicates in the table. This is for Academic Year
  for(i = 0; i < globalArrayOfStudents.length; i++){
    if(globalArrayOfStudents[i].stuName == studentDict.stuName){
      $("#warningModalText").html("You have already entered a labor status form for " + studentDict.stuName + " in the table below.");
      $("#warningModal").modal("show");
      return true;
    }
  }
  return false;
}

function checkPrimaryPositionToCreateTheTable(studentDict) {
  var term = $("#selectedTerm").val();
  var termName = $('#selectedTerm').find('option:selected').text();
  var url = "/laborstatusform/getstudents/" + term + "/" + studentDict.stuBNumber;
  var data = JSON.stringify(studentDict.stuJobType);
  $.ajax({
    method: "POST",
    url: url,
    data: data,
    dataType: "json",
    contentType: "application/json",
    success: function(response) {
      switch (response["status"]) {
        case "hire":
          initialLSFInsert(studentDict);
          break
        case "noHireForSecondary":
          $("#warningModalTitle").html("Insert Rejected");
          $("#warningModalText").html(studentDict.stuName + " needs an approved primary position for " + termName + " before a secondary position can be added.");
          $("#warningModal").modal("show");
          break;
        default:
          $("#releaseRehireModalTitle").html("Insert Rejected");
          $('#studentName').html(studentDict.stuName)
          $('#oldTerm').html(response['term'])
          $('#oldSupervisor').html(response['primarySupervisor'])
          $('#oldDepartment').html(response['department'])
          $('#oldPosition').html(response['position'])
          $('#oldHours').html(response['hours'])

          $('#newTerm').html($("#selectedTerm").find("option:selected").text());
          $('#newSupervisor').html(studentDict.stuSupervisor)
          $('#newDepartment').html(studentDict.stuDepartment +" ("+ studentDict.stuDepartmentORG+"-"+studentDict.stuDepartmentAccount +")")
          $('#newPosition').html(studentDict.stuPositionCode +" - "+ studentDict.stuPosition +" ("+ studentDict.stuWLS+")")
          $('#newHours').html(studentDict.stuJobType +" ("+ studentDict.stuWeeklyHours+")")

          if(response["approvedForm"] && response["isLaborAdmin"]){
            $('#bannerWarning').show();
            $('#rehireReleaseButton').show();

            $('#warningCheckbox').click(function(){
              $('#rehireReleaseButton').prop("disabled", !$('#warningCheckbox').prop('checked'));
            });

          }
          else{
            $('#rehireReleaseButton').hide();
            $('#bannerWarning').hide();
          }
          $("#releaseRehireModal").modal("show");
          break;
      }
     }
   });
 }


function initialLSFInsert(studentDict){ //Add student info to the table if they have no previous lsf's in the database
  if (checkDuplicate(studentDict) == false){
      checkTotalHours(studentDict);
      createAndFillTable(studentDict, reviewButtonFunctionality);
  }
}

function createAndFillTable(studentDict, callback=null) {
  globalArrayOfStudents.push(studentDict);
  if(callback){
    callback()
  }
  document.cookie = JSON.stringify(globalArrayOfStudents) + ";max-age=28800;";
  $("#mytable").show();
  $("#jobTable").show();
  $("#hoursTable").show();
  var isBreak = (studentDict).isTermBreak;
  var table = document.getElementById("mytable").getElementsByTagName("tbody")[0]; //This one needs document.getElementById, it won't work without it
  if (!isBreak) {
    var notesID0 = String((studentDict).stuName + (studentDict).stuJobType + (studentDict).stuPosition);
    var notesID1 = notesID0.replace(/ /g, "");
    //var notesID2 = notesID1.substring(0, notesID1.indexOf("("));
  }
  else {
    var selectedContractHoursName = $("#selectedContractHours").val();// For whatever reason this is undefined
  }
  var notesGlyphicon = "<a href=\"#\" data-toggle=\"modal\" tabindex=\"0\" aria-label=\"View Notes\" onclick = \"showNotesModal(this)\" id= \"nGlyphicon\" ><span class=\"glyphicon glyphicon-edit\"></span></a>";
  var removeIcon = "<a href=\"#\" onclick= \"deleteRow(this)\" tabindex=\"0\" aria-label=\"Remove Row\" id=\"rGlyphicon\"><span class=\"glyphicon glyphicon-remove\" style=\"color:red;\"></span></a>";
  var row = table.insertRow(-1);
  var cell1 = row.insertCell(0);
  var cell2 = row.insertCell(1);
  var cell3 = row.insertCell(2);
  var cell4 = row.insertCell(3);
  var cell5 = row.insertCell(4);
  var cell6 = row.insertCell(5);
  var cell7 = row.insertCell(6);
  $(cell1).html((studentDict).stuName + " (" + ((studentDict).stuBNumber).trim()+ ")");
  $(cell2).html((studentDict).stuPosition + " (" + (studentDict).stuWLS + ")");
  $(cell2).attr("data-posn", (studentDict).stuPositionCode);
  $(cell2).attr("data-wls", (studentDict).stuWLS);
  cell2.id="position_code";
  if (!isBreak) {
    hours = studentDict.stuWeeklyHours;
    studentDict.stuContractHours = null;
  }
  else{
    hours = studentDict.stuContractHours;
    studentDict.stuWeeklyHours = null;
  }
  $(cell3).html(studentDict.stuJobType);
  $(cell4).html(hours);
  $(cell5).html((studentDict).stuStartDate + " - " + (studentDict).stuEndDate);
  $(cell6).html(notesGlyphicon);
  $(cell7).html(removeIcon);


  $("#student").val("default");
  $("#student").selectpicker("refresh");
  if (globalArrayOfStudents.length >= 1) {
    $("#reviewButton").show();
  }
}


function isOneLaborStatusForm(studentDict){
  var isBreak = (studentDict).isTermBreak;
  var term = $("#selectedTerm").val();
  if(isBreak){
    url = "/laborstatusform/getstudents/" + term + "/"+ studentDict.stuBNumber+ "/"+ 'isOneLSF';
    // check whether student has multiple labor status forms over the break period.
    $.ajax({
      url: url,
      dataType: "json",
      success: function (response){
        if(response["showModal"] == true){
        // if they already have one lsf or multiple then show modal reminding the new supervisor of 40 hour mark rule.
          var names = ""
          response["previousSupervisorNames"].forEach(element => names += element + ', ');
          supervisorsNames = names.trim().replace(/.$/,".")

          $("#warningModalTitle").text("Warning");
          $("#warningModalText").html("<strong>"+response["studentName"] + " is already working with " +
                                          supervisorsNames +"</strong><br><br>" +
                                          "Students may only work up to 40 hours a week during break periods.");
          $("#warningModal").modal('show');
        }
      }
    });
  }
}

function checkTotalHours(studentDict) {
  var termCode = $("#selectedTerm").val()
  var isBreak = $("#selectedTerm").find("option:selected").data("termbreak");
  var hours = studentDict.stuWeeklyHours
  if (isBreak) {
    hours = studentDict.stuContractHours
  }
  $.ajax({
    url: "/laborstatusform/checktotalhours/" + termCode +"/"+ studentDict.stuBNumber +"/"+ hours,
    dataType: "json",
    success: function (response){
      if (response > (15) && !isBreak) {
        studentDict.isItOverloadForm = "True";
        $("#OverloadModal").modal('show');
      }
      studentDict.stuTotalHours = response;
      return true;
    }
  });
}


//Triggered when summer labor is clicked when making a New Labor Status Form
function summerLaborWarning(){
  var isBreak = $("#selectedTerm").find("option:selected").data("termbreak");
  var isSummer = $("#selectedTerm").find("option:selected").data("termsummer");
  if (isSummer){
    $("#SummerContract").modal('show');
    return true;
    //checks if any break has been clicked and generates a modal
  } else if (isBreak && !isSummer){
      $("#warningModalTitle").html("Reminder");
      $("#warningModalText").html("Students may only work up to 40 hours a week during break periods.");
      $("#warningModal").modal('show');
      return true;
  } else {
      return true;
        }
}

function pageResetConfirmation() {
    // Pops up modal for confirming that the user wants to reset the page
    $("#warningModal").modal('show');
    $("#warningModalTitle").html("Reset Confirmation");
    $("#warningModalText").html("<p>This action will remove all forms in the table \
                                 and empty all form fields.</p>");
    $("#warningModalButton").hide();
    $("#resetConfirmButton").show();
}

$("#resetConfirmButton").click(function(){
    // Handles page reset from confirmation modal
    $("#warningModal").modal('hide');
    globalArrayOfStudents = [];
    $("#tbodyid tr").remove();
    document.cookie = JSON.stringify(globalArrayOfStudents) + ";max-age=0;";
    location.reload();
});

function reviewButtonFunctionality() { // Triggred when Review button is clicked and checks if fields are filled out.
  $("#laborStatusForm").on("submit", function(e) {
    e.preventDefault();
  });
  if (globalArrayOfStudents.length >= 1) {
    $("#submitmodalid").show();
    $("#doneBtn").hide();
    disableTermSupervisorDept();
    createModalContent();
  }
}

function createModalContent() { // Populates Submit Modal with Student information from the table
  var isBreak = $('#selectedTerm').find('option:selected').data('termbreak');
  modalList = [];
  $("#closeBtn").show();
  if (isBreak){
    for (var i = 0; i < globalArrayOfStudents.length; i++) {
      var bigString = "<li>" + globalArrayOfStudents[i].stuName + " | " + globalArrayOfStudents[i].stuPosition + " | " +
                      globalArrayOfStudents[i].stuContractHours + " hours";
      modalList.push(bigString);
    }
    $("#SubmitModalText").html("Labor status form(s) will be submitted for:<br><br>" +
                                                            "<ul style=\"display:inline-block;text-align:left;\">" +
                                                            modalList.join("</li>")+"</ul>"+
                                                            "<br><br>The labor status form will be eligible for approval in one business day.");
    $("#SubmitModal").modal("show");
  }
  else {
    for (var i = 0; i < globalArrayOfStudents.length; i++) {
      var bigString = "<li>" + globalArrayOfStudents[i].stuName + " | " + globalArrayOfStudents[i].stuPosition +
                      " | " + globalArrayOfStudents[i].stuJobType + " | " + globalArrayOfStudents[i].stuWeeklyHours + " hours";
      modalList.push(bigString);
    }
    $("#SubmitModalText").html("Labor status form(s) will be submitted for:<br><br>" +
                               "<ul style=\"display: inline-block;text-align:left;\">" +
                               modalList.join("</li>")+"</ul>"+
                               "<br><br>The labor status form will be eligible for approval in one business day.");
    $("#SubmitModal").modal("show");
  }
}

// userInsert() sends SubmitModal's info to controller using ajax and gets the response in array containing true(s) or/and false(s)
function userInsert(){
    $("#laborStatusForm").on("submit", function(e) {
      e.preventDefault();
    });

    $("#submitmodalid").prop("disabled", true);
    $("#closeBtn").prop("disabled", true);
    $("#submitmodalid").text("Processing...");
    $("#SubmitModal").data("bs.modal").options.backdrop = "static";
    $("#SubmitModal").data("bs.modal").options.keyboard = false;

    $.ajax({
           method: "POST",
           url: "/laborstatusform/userInsert",
           data: JSON.stringify(globalArrayOfStudents),
           contentType: "application/json",
           success: function(response) {
               var isBreak = $('#selectedTerm').find('option:selected').data('termbreak');
               modalList = [];
               for(var key = 0; key < globalArrayOfStudents.length; key++){
                   var studentName = globalArrayOfStudents[key].stuName;
                   var position = globalArrayOfStudents[key].stuPosition;
                   var selectedContractHours = globalArrayOfStudents[key].stuContractHours;
                   var jobType = globalArrayOfStudents[key].stuJobType;
                   var hours = globalArrayOfStudents[key].stuWeeklyHours;

                   if (response.includes(false)){ // if there is even one false value in response
                       // var selectedContractHours = globalArrayOfStudents[key].stuWeeklyHours;
                       if (response[key] === false){ // Finds the form that has failed.
                           if (isBreak){
                              display_failed.push(key);
                              var bigString = "<li>" +"<span class=\"glyphicon glyphicon-remove\" style=\"color:red\"></span> " + studentName + " | " + position + " | " + selectedContractHours + " hours";
                           }
                           else {
                              display_failed.push(key);
                              var bigString = "<li>"+"<span class=\"glyphicon glyphicon-remove\" style=\"color:red\"></span> " + studentName + " | " + position + " | " + jobType + " | " + hours + " hours";
                           }
                       }
                       else{
                            if (isBreak){
                                var bigString = "<li>" +"<span class=\"glyphicon glyphicon-ok\" style=\"color:green\"></span> " + studentName + " | " + position + " | " + selectedContractHours + " hours";
                            }
                            else {
                                var bigString = "<li>"+"<span class=\"glyphicon glyphicon-ok\" style=\"color:green\"></span> " + studentName + " | " + position + " | " + jobType + " | " + hours + " hours";
                            }
                       }
                    modalList.push(bigString);
                   $("#SubmitModalText").html("Some of your submitted Labor Status Form(s) did not succeed:<br><br>" +
                                              "<ul style=\"list-style-type:none; display: inline-block;text-align:left;\">" +
                                               modalList.join("</li>")+"</ul>"+""
                                            );
                   $("#closeBtn").hide();
                   $("#SubmitModal").modal("show");
                 }
               else{
                    if (isBreak){
                    var bigString = "<li>" +"<span class=\"glyphicon glyphicon-ok\" style=\"color:green\"></span> " + studentName + " | " + position + " | " + selectedContractHours + " hours";
                  }
                    else{
                    var bigString = "<li>"+"<span class=\"glyphicon glyphicon-ok\" style=\"color:green\"></span> " + studentName + " | " + position + " | " + jobType + " | " + hours + " hours";
                  }
                 modalList.push(bigString);
                 $("#SubmitModalText").html("Labor Status Form(s) succeeded:<br><br>" +
                                            "<ul style=\"list-style-type:none; display: inline-block;text-align:left;\">" +
                                             modalList.join("</li>")+"</ul>"+""
                                          );
                 $("#closeBtn").hide();
                 $("#SubmitModal").modal("show");
                 $("#reviewButton0").prop('disabled',true);
                 $("#addMoreStudent").prop('disabled',true);
                 $("a").attr("onclick", "").unbind("click");
                 $(".glyphicon-edit").css("color", "grey");
                 $(".glyphicon-remove").css("color", "grey");
                 parsedArrayOfStudentCookies = document.cookie;
                 document.cookie = parsedArrayOfStudentCookies +";max-age=0";
                 window.location.replace("/laborstatusform");
               }
             }
             $("#submitmodalid").prop("disabled", false);
             $("#closeBtn").prop("disabled", false);
             $("#submitmodalid").text("Submit");
             $("#SubmitModal").data("bs.modal").options.backdrop = true;
             $("#SubmitModal").data("bs.modal").options.keyboard = true;

             $("#submitmodalid").hide();
             $("#doneBtn").show();
            }
         }); // ajax closing tag

      document.getElementById("doneBtn").onclick = function() { // Calls this function after failed form(s)
       if (display_failed.length > 0){
           $('#error_modal').empty();
           $('#error_modal').append('<p style="padding-left:16px;"><b>ERROR:</b> Contact Systems Support if form(s) continue to fail <span style="color:darkred;" class="glyphicon glyphicon-exclamation-sign"></span> </p>');
           msgFlash("The form(s) below failed to submit, please try again.", "fail");
            var failed_students = globalArrayOfStudents.filter(function(item, indx){
                if (display_failed.includes(indx)){
                 return item;
                }
            });
           globalArrayOfStudents = [];
           $('#tbodyid').empty();
           failed_students.forEach(function(item){
              createAndFillTable(item);
           });
           $('#SubmitModal').modal('hide');
           display_failed=[];
         }
      }
} // userInsert closing tag

$("#submitmodalid").click(function() {
    $('html,body').scrollTop(0);    //This makes the screen scroll to the top if it is not already so the user can see the flash message.
});

function releaseAndRehire(){
  var studentDict = createStuDict();
  data = JSON.stringify(studentDict)
  $.ajax({
    method:"POST",
    url:"/laborStatusForm/modal/releaseAndRehire",
    data: data,
    contentType: "application/json",
    success: function(response){
      if (response["Success"]) {
        window.location.replace("/laborstatusform");
      }
    }
  })

}

function intializeDataTable() {
  var lsfTable = $('#lsfTable').DataTable({
    paging: true,
    ordering: false,
    info: false,
    responsive: true,
    searching: false,
        ajax: {
          url: "/lsfdatatable",
          type: "GET",
        columns: [
            { data: 'Student' },
            { data: 'Position (WLS)' },
            { data: 'Job Type' },
            { data: 'Hours' },
            { data: 'Term' },
            { data: 'Contract Dates' },
            { data: 'Notes'},
            { data: 'Edit'}
        ],
      }
    });
  };
