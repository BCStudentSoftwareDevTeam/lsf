function overloadSubmission(formHistoryKey){
  // this function will update the notes and status in the db
  var notesContent = $("#denyReason_"+formHistoryKey).val()
  denialInfoDict = {}
  denialInfoDict["formHistoryID"] = formHistoryKey
  denialInfoDict["denialNote"] = notesContent
  data = JSON.stringify(denialInfoDict)

  if($(".textarea-required").prop("required") == true && notesContent == " "){
    $("#finOverloadSubmit").removeAttr("data-dismiss")
    $(".textarea-required").focus();
    $("#required-error").show();
  }
  else{
    $("#required-error").hide();
    $("#finOverloadSubmit").attr("data-dismiss", "modal")
    $.ajax({
      method: "POST",
      url:"/admin/financialAidOverloadApproval/"+statusName,
      datatype: "json",
      data: data,
      contentType: "application/json",
      success:function(){
        msgFlash("Your changes have been saved successfully. Thank you. You will be redirected shortly.", "success")
        setTimeout(function() { // executed after 1 second
           window.location.replace('/'); // redirects to a new website
         }, 5000);
      },
      error:function(response){
        console.log("error", response);
      }
    });
  }
}

// for showing different messages with flash
function msgFlash(flash_message, status){
    category = (status === "success") ? "success" : "danger";
    $("#flash_container").prepend("<div class=\"alert alert-"+ category +"\" role=\"alert\" id=\"flasher\">"+flash_message+"</div>");
    $("#flasher").delay(5000).fadeOut();

}
var statusName = null
function openApproveDenyModal(status){
  statusName = status
  if (status == "approved"){
    $("#required-error").hide();
    $("#finOverloadSubmit").attr("data-dismiss", "modal")
    $("#finOverloadModal .modal-title").text("Reason for Approval")
    $("#modal-body-content").html("You are approving this student's Overload Request. You can optionally provide a reason for this decision. <br><br><b>Please leave a note if the overload form is being approved for a different term.</b>");
    $(".textarea-required").prop('required', false);
    $("#finOverloadModal").modal("show");
  }
  else{
    $("#finOverloadModal .modal-title").text("Reason for Denial");
    $("#modal-body-content").html("You are denying this student's Overload Request. Please provide a reason for this decision.");
    $(".textarea-required").prop('required', true);
    $("#finOverloadModal").modal("show");
  }
}

function overloadNoteInsert(textareaID, buttonID) {
  var overloadNotes = $("#" + textareaID).val();
  var data = JSON.stringify(overloadNotes);
  $("#" + buttonID).on('submit', function(e) {
    e.preventDefault();
  });

  $.ajax({
    method: "POST",
    url: '/admin/notesInsert/' + textareaID,
    data: data,
    contentType: 'application/json',
    success: function(response) {
        location.reload(true);
      }
  });
}
