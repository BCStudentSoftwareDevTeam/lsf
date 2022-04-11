// Opens collapse menu for this page
$("#admin").collapse("show");

$('a.hover_indicator').click(function(e){
  e.preventDefault(); // prevents click on '#' link from jumping to top of the page.
});

$(document).ready(function() {
  // If the overload tab has been selected, then we need to restrict the
  // ordering functionality on different headers

  if ($('#overloadTab').hasClass('active') || $('#releaseTab').hasClass('active') || $('#completedOverloadTab').hasClass('active')) {
    targetsList = [8]
  } else if ($('#adjustedTab').hasClass('active')) {
    targetsList = [0, 10]
  } else {
    targetsList = [0, 9]
  }
  // If overload tab has been clicked, then we
  table = $('#pendingForms, #statusForms, #adjustedForms, #releaseForms').DataTable({
    'columnDefs': [{
      'orderable': false,
      'targets': targetsList
    }], // hide sort icon on header of first column
    // 'columnDefs': [{ 'orderable': false, 'targets': 9 }],
    'aaSorting': [
      [1, 'asc']
    ], // start to sort data in second column
    pageLength: 50,
    // "dom": '<"top"fl>rt<"bottom"p><"clear">'
  });

// CHECK ALL CHECKBOX ON APPROVE BUTTON
  $('#checkAll').change(function(){
    $(".approveCheckbox").prop('checked', $(this).prop("checked"));
  });

  $('.approveCheckbox').change(function(){
	   //uncheck "check all" if one of the listed checkbox item is unchecked
  	if(this.checked == false){
  		$("#checkAll")[0].checked = false;
    }
  	 //check "check all" if all checkbox items are checked
  	if ($('.approveCheckbox:checked').length == $('.approveCheckbox').length ){
  		  $("#checkAll")[0].checked = true;
  	}
  });

});

var labor_details_ids = []; // for insertApprovals() and final_approval() only
function insertApprovals(laborHistoryId = null) {
  var getChecked = table.$('.approveCheckbox:checked').each(function() {
    labor_details_ids.push(this.value);
  });
  // This 'if' statement is used on the formSearch table where we can approve forms one-by-one only
  if (laborHistoryId) {labor_details_ids.push(laborHistoryId)}
  //this checks wether the checkbox is checked or not and if does not it disable the approve selected button
  var atLeastOneIsChecked = $('input[name="check[]"]:checked').length > 0;
  if (!atLeastOneIsChecked && !laborHistoryId) {
    $("#approveSelected").prop("disabled", true);
    $("#approvePendingForm").prop("disabled", true);
    $("#adjustedApproval").prop("disabled", true);
    $("#approveOverload").prop("disabled", true);
    $("#approveRelease").prop("disabled", true);

    location.reload();
  }
  var data = JSON.stringify(labor_details_ids);
  $.ajax({
    type: "POST",
    url: "/admin/checkedForms",
    datatype: "json",
    data: data,
    contentType: 'application/json',
    success: function(response) {
      if (response) {
        var returned_details = response;
        updateApproveTableData(returned_details);
      }
    }
  });
}
//this method adds data to each row in the approve selected Modal
function updateApproveTableData(returned_details) {
  for (var i = 0; i < returned_details.length; i++) {
    var student = returned_details[i][0];
    var department = returned_details[i][1];
    var position = returned_details[i][2];
    var r_hour = returned_details[i][3];
    var c_Hours = returned_details[i][4];
    var supervisor = returned_details[i][5];
    var hours = " ";
    if (r_hour.length == 4) {
      hours = c_Hours;
    } else {
      hours = r_hour;
    }
    $('#classTableBody').append('<tr><td>' + student + '</td><td>' + department + '</td><td>' + position + '</td><td> ' + hours + '</td> <td> ' + supervisor + '</td></tr>');
  }
}

$('#approvalModal').on('hidden.bs.modal', function () {// Makes the close functionality work when clicking outside of the modal
  approvalModalClose();
});

function approvalModalClose(){// on close of approval modal we are clearing the table to prevent duplicate data.
  $('#classTableBody').empty();
  labor_details_ids = [] // emptying the list, becuase otherwise will cause duplicate data.
}

function finalApproval() { //this method changes the status of the lsf from pending to approved status
  $(".btn").prop("disabled", true);
  $(".close").prop("disabled", true);
  $("#approveModalButton").text("Processing...");
  $("#approvalModal").data("bs.modal").options.backdrop = "static";
  $("#approvalModal").data("bs.modal").options.keyboard = false;
  var data = JSON.stringify(labor_details_ids);
  $.ajax({
    type: "POST",
    url: "/admin/updateStatus/approved",
    datatype: "json",
    data: data,
    contentType: 'application/json',
    success: function(response) {
      if (response) {
        if (response.success) {
          $(".btn").prop("disabled", false);
          $(".close").prop("disabled", false);
          $("#approveModalButton").text("Approve");
          $("#approvalModal").data("bs.modal").options.backdrop = true;
          $("#approvalModal").data("bs.modal").options.keyboard = true;

          // Try and catch is used here to prevent General Search page from reloading the entire the page.
          try {
            runformSearchQuery();
            $('#approvalModal').modal('hide');
          }
          catch(e){
            location.reload(true);
          }
        }
      }
    }
  });
}

var laborDenialInfo = []; //this arrary is for insertDenial() and finalDenial() methods
//This method calls AJAX from checkforms methods in the controller
function insertDenial(val) {
  laborDenialInfo.push(val);
  var data = JSON.stringify(laborDenialInfo);
  $.ajax({
    type: "POST",
    url: "/admin/checkedForms",
    datatype: "json",
    data: data,
    contentType: 'application/json',
    success: function(response) {
      if (response) {
        var labor_denial_detials = response;
        finalDenial_data(labor_denial_detials);
      }
    }
  });
}

// this method inserts data to the table of denial popup modal
function finalDenial_data(returned_details) {
  for (var i = 0; i < returned_details.length; i++) {
    var student = returned_details[i][0];
    var department = returned_details[i][1]
    var position = returned_details[i][2];
    var r_hour = returned_details[i][3];
    var c_Hours = returned_details[i][4];
    var supervisor = returned_details[i][5];
    var hours = " ";
    if (r_hour.length == 4) {
      hours = c_Hours;
    } else {
      hours = r_hour;
    }
    $('#denialPendingFormsBody').append('<tr><td>' + student + '</td><td>' + department + '</td><td>' + position + '</td><td> ' + supervisor + '</td> <td> ' + hours + '</td></tr>'); //populate the denial modal for all pending forms
  }
}

function denialModalClose(){// on close of denial modal we are clearing the table to prevent duplicate data.
  $('#denialPendingFormsBody').empty();
  laborDenialInfo = [] // emptying the list, becuase otherwise will cause duplicate data.
}

$('.denialModal').on('hidden.bs.modal', function () {// makes the close functionality work when clicking otuside of the modal
  denialModalClose();
});



function finalDenial() { // this mehod is AJAX call for the finalDenial method in python file
  var data = JSON.stringify(laborDenialInfo);
  $.ajax({
    type: "POST",
    url: "/admin/updateStatus/denied",
    datatype: "json",
    data: data,
    contentType: 'application/json',
    success: function(response) {
      if (response) {
        if (response.success) {
          // Try and catch is used here to prevent General Search page from reloading the entire the page.
          try {
            runformSearchQuery();
            $('.denialModal').modal('hide');
          }
          catch(e){
            location.reload(true);
          }
        }
      }
    }
  });
}

function getNotes(formId) {
  $.ajax({
    type: "GET",
    url: "/admin/getNotes/" + formId,
    datatype: "json",
    success: function(response) {
      if ("Success" in response && response.Success == "false") {
        //Clears supervisor notes p tag and the labor notes textarea
        $(".notesText").empty();
        $("#laborNotesText").empty();
      } else {
        $("#laborNotesText").data('formId', formId); //attaches the formid data to the textarea

        //Populates notes value from the database
        if ("supervisorNotes" in response) {
          $(".supeNotesLabel").show()
          $(".notesText").show()
          $(".notesText").html(response.supervisorNotes);
        }
        if (!("supervisorNotes" in response)) {
          $(".supeNotesLabel").hide()
          $(".notesText").hide()
        }
        if ("laborDepartmentNotes" in response) {
          $(".notesLogArea").html(response.laborDepartmentNotes);
        } else if (!("laborDepartmentNotes" in response)) {
          $(".notesLogArea").html("No notes to show")
        }
      }
    }
  });
}

function notesInsert(textareaID, buttonID) {
  var formId = $("#" + textareaID).data('formId');
  var laborNotes = $("#" + textareaID).val(); //this is getting the id of the labor notes text area
  var notes = {
    'formId': formId,
    'notes': laborNotes
  }; // {ID: textarea value} this sets the text area to what the user types in it
  formId = notes.formId; //This is how we get the ID of the form
  var note = notes.notes; //This is how we are getting the note object from the dictionary
  var data = JSON.stringify(note);

  $("#" + buttonID).on('submit', function(e) {
    e.preventDefault();
  });

  $.ajax({
    method: "POST",
    url: '/admin/notesInsert/' + formId,
    data: data,
    contentType: 'application/json',
    success: function(response) {
      // Try and catch is used here to prevent General Search page from reloading the entire the page.
      try {
        clearTextArea();
        runformSearchQuery();
        $('#NotesModal').modal('hide');
      }
      catch(e){
        location.reload(true);
      }
      }
  });
}



function finalDeny() {
  /*
  This method will first check if the deny reason text area has been populated, and if
  it is then the method to update the form with the reject reason will be called
  */
  var denyReason = $('#denyReason').val()
  if (denyReason == '') {
    $('#denyReason').attr("placeholder", 'A reason for denial is required to deny the form')
    $('#denyReason').css('border-color', 'red');
  } else {
    laborDenialInfo.push(denyReason)
    finalDenial();
  }
}

function clearTextArea() { //makes sure that it empties text areas and p tags when modal is closed
  $("#notesText").val("");
  $("#laborNotesText").val("");
}


function loadOverloadModal(formHistoryID, laborStatusFormID) {
  /*
  This method sends an AJAX call to recieve data used to populate
  the overload modal.
  */
  $("#overloadModal").modal("show");
  $("#overloadModal").find('.modal-content').load('/admin/overloadModal/' + formHistoryID);
}

function loadReleaseModal(formHistoryID, laborStatusFormID) {
  $("#modalRelease").modal("show");
  $("#modalRelease").find('.modal-content').load('/admin/releaseModal/' + formHistoryID);

}

function displayModalTextArea(radioValue) {
  /*
  This method toggles the 'Deny' and 'Admin Notes' textareas for the
  'Overload' and 'Release' modals based on what radio has been selected
  */
  $('.status-warning').hide();
  var radioVal = radioValue
  if (radioVal == 'deny') {
    $('.finalNote').val('');
    $('#banner-warning').hide();
    $('.denyTextArea').css('display', 'block')
    $('.notesTextArea').css('display', 'none')
    $("#denyTextAreaOverload").addClass("has-error");
  } else {
    $('.finalDeny').val('');
    $('#banner-warning').show();
    $('.denyTextArea').css('display', 'none')
    $('.notesTextArea').css('display', 'block')
    $("#denyTextAreaOverload").removeClass("has-error");
  }
}

function sendEmail(formHistoryID, emailRecipient) {
  /*
  This method sends data to the backend that it used to send an email,
  and also updates the data inside of the overload modal
  */
  emailTrackerInfo = {
    'formHistoryID': formHistoryID,
    'emailRecipient': emailRecipient
  }
  data = JSON.stringify(emailTrackerInfo)
  $.ajax({
    method: "POST",
    url: '/admin/sendVerificationEmail',
    data: data,
    contentType: 'application/json',
    success: function(response) {
      var newDate = response['emailDate']
      var status = response['status']
      var recipient = response['recipient']
      if (recipient == 'SAAS') {
        $("#statusSAAS").html(status)
        $("#emailDateSAAS").html(newDate)
      } else if (recipient == 'Financial Aid') {
        $("#statusFinancialAid").html(status)
        $("#emailDateFinancialAid").html(newDate)
      }
    },
    error: function(request, status, error) {
      console.log(request.responseText);
    }
  });
}

function submitOverload(formHistoryID, isLaborAdmin) {
  /*
  This method is used to check if the form is ready for submission, then
  makes an AJAX call with the information needed to complete the submission
  */
  if ($('input[name=decision]:checked').length > 0) {
    var createAJAX = true
    var status = 'Pending'
    var overloadModalInfo = {
      'formHistoryID': formHistoryID
    }
    if ($('#deny').is(':checked')) {
      if ($("#denyOverloadReason").val() == "") {
        $("#denyOverloadReason").focus();
        $("#required-error").show();
        createAJAX = false
      } else {
        $('#required-error').hide();
        status = 'Denied'
        var denyReason = $('#denyOverloadReason').val()
        overloadModalInfo['denialReason'] = denyReason;
      }
    } else {
      if ($('#approve').is(':checked')) {
        status = 'Approved';
      }
      if ($('#approveRel').is(':checked')) {
        status = 'Approved Reluctantly'
      }
      if ($('#overloadNotes').val() != '') {
        var adminNotes = $('#overloadNotes').val()
        overloadModalInfo['adminNotes'] = adminNotes;
      }
    }

    if ($('#initials').val() == ""){
      createAJAX = false
      $('.status-warning').html('<span class="glyphicon glyphicon-exclamation-sign"></span><strong> Please fill out all required fields.</strong>')
      $('.status-warning').show();
    }
    else{
      createAJAX = true
      $('.status-warning').hide();
      overloadModalInfo['initials'] = $('#initials').val();
    }

    if (createAJAX == true) {
      overloadModalInfo['status'] = status;
      overloadModalInfo['formType'] = 'Overload';
      var data = JSON.stringify(overloadModalInfo)
      $.ajax({
        method: "POST",
        url: '/admin/modalFormUpdate',
        data: data,
        contentType: 'application/json',
        success: function(response) {
          // Try and catch is used here to prevent General Search page from reloading the entire the page.
          try {
            runformSearchQuery();
            $('#overloadModal').modal('hide');
          }
          catch(e){
            location.reload(true);
          }
        },
        error: function(request, status, error) {
          console.log(request.responseText);
        }
      });
    }
  } else {
    $('.status-warning').show();
  }
}

function submitRelease(formHistoryID) {
  /*
  This method is used to check if the form is ready for submission, then
  makes an AJAX call with the information needed to complete the submission
  */
  if ($('input[name=decision]:checked').length > 0) {
    var createAJAX = true
    var status = 'Pending'
    var releaseModalInfo = {
      'formHistoryID': formHistoryID
    }
    if ($('#denyRelease').is(':checked')) {
      if ($("#denyReleaseReason").val() == "") {
        $("#denyReleaseReason").focus();
        $(".required-error").show();
        createAJAX = false;
      } else {
        $('.required-error').hide();
        status = 'Denied';
        var denyReason = $('#denyReleaseReason').val();
        releaseModalInfo['denialReason'] = denyReason;
      }
    } else {
      if ($('#approveRelease').is(':checked')) {
        status = 'Approved';
      }
      if ($('#releaseNotes').val() != '') {
        var adminNotes = $('#releaseNotes').val();
        releaseModalInfo['adminNotes'] = adminNotes;
      }
    }
    if (createAJAX == true) {
      releaseModalInfo['status'] = status;
      releaseModalInfo['formType'] = "Release";
      var data = JSON.stringify(releaseModalInfo)
      $.ajax({
        method: "POST",
        url: '/admin/modalFormUpdate',
        data: data,
        contentType: 'application/json',
        success: function(response) {
          // Try and catch is used here to prevent General Search page from reloading the entire the page.
          try {
            runformSearchQuery();
            $('#modalRelease').modal('hide');
          }
          catch(e){
            location.reload(true);
          }
        },
        error: function(request, status, error) {
          console.log(request.responseText);
        }
      });
    }
  } else {
    $('.status-warning').show();
  }
}

function toggleNotesLog(laborStatusFormID, formHistoryID) {
  /*
  This method toggles the 'Notes' log at the bottom of the
  'Overload' and 'Release' modal to show/hide it
  */
  if ($('.logNotesDiv').css('display') == 'none') {
    var modalViewNotesID = '#modalNote_' + String(formHistoryID)
    $(modalViewNotesID).html('Hide Notes')
    getNotes(laborStatusFormID)
    $('.logNotesDiv').css('display', 'block')
  } else {
    notesCounter(laborStatusFormID, formHistoryID)
    $('.logNotesDiv').css('display', 'none')
  }
}

function notesCounter(laborStatusFormID, formHistoryID){
  /*
  This method displays the number of admin notes a Labor
  Status Form has
  */
  var data = {'laborStatusFormID': laborStatusFormID}
  data = JSON.stringify(data)
  $.ajax({
    method: "POST",
    url: '/admin/notesCounter',
    data: data,
    contentType: 'application/json',
    success: function(response) {
      var viewNotesID = '#notes_' + String(formHistoryID)
      var modalViewNotesID = '#modalNote_' + String(formHistoryID)
      $(viewNotesID).html('View Notes (' + response['noteTotal'] + ')')
      $(modalViewNotesID).html('View Notes (' + response['noteTotal'] + ')')
    },
    error: function(request,status,error){
      console.log(request.responseText);
    }
  });
}
