// Opens collapse menu for this page
$("#admin").collapse("show");

let emailTemplateArray;

$(document).ready(function() {
  getEmailArray();
});

function getEmailArray() {
  $.ajax({
    url: "/admin/emailTemplates/getEmailArray/",
    dataType: "json",
    success: function(response) {
      emailTemplateArray = response;
      prefillFromQueryParams();
    }
  })
}

function prefillFromQueryParams() {
  // Allows deep-linking into this page (e.g. from another admin page's
  // "Edit Email Template" button) with the Recipient/Form Type/Action
  // selectpickers pre-selected, so the template loads without the admin
  // having to click through the cascading dropdowns manually.
  var params = new URLSearchParams(window.location.search);
  var recipient = params.get("audience");
  var formType = params.get("formType");
  var action = params.get("action");
  if (!recipient) {
    return;
  }

  // populatePurpose() ends by inserting the body into the CKEditor instance,
  // which initializes asynchronously (CKEDITOR.replace() in emailTemplates.html).
  // Running this cascade immediately on page load (unlike a human clicking
  // through the dropdowns) can race ahead of that, so wait for the editor
  // to be ready before touching it.
  function runPrefill() {
    $("#recipient").val(recipient).selectpicker("refresh");
    populateFormType();

    if (formType) {
      $("#formType").val(formType).selectpicker("refresh");
      populateAction();

      if (action) {
        $("#action").val(action).selectpicker("refresh");
        populatePurpose();
      }
    }
  }

  // CKEDITOR.instances["editor1"] is registered as soon as CKEDITOR.replace()
  // is called, well before the editor is actually ready to accept content
  // (that's the "ready" status). Checking mere existence isn't enough here.
  var editor = CKEDITOR.instances["editor1"];
  if (editor && editor.status === "ready") {
    runPrefill();
  } else if (editor) {
    editor.on("instanceReady", runPrefill);
  } else {
    CKEDITOR.on("instanceReady", function(evt) {
      if (evt.editor.name === "editor1") {
        runPrefill();
      }
    });
  }
}

function populateFormType() {
  // populates Form Type only when Recipient is selected
  $("#formType").prop("disabled", false);
  $("#formType").empty();
  $("#action").empty();
  $("#subject").val("");
  let recipient = $("#recipient").val();
  let appendedItems = [];
  for (let dict in emailTemplateArray) {
    let value = emailTemplateArray[dict]["formType"];
    if (recipient == emailTemplateArray[dict]["audience"] && !appendedItems.includes(value)) {
      appendedItems.push(value);
      $("#formType").append('<option value="' + value + '">' + value + '</option>');
    }
  }
  $("#formType").selectpicker("refresh");
  $("#action").selectpicker("refresh");
  $("#subject").selectpicker("refresh");
  $("#action").prop("disabled", true);
  $("#subject").prop("disabled", true);
}

function populateAction() {
  // populates Action only when Form Type is selected
  $("#action").prop("disabled", false);
  $("#action").empty();
  $("#subject").val("");
  let recipient = $("#recipient").val();
  let formType = $("#formType").val();
  let appendedItems = [];
  for (let dict in emailTemplateArray){
    let value = emailTemplateArray[dict]["action"];
    if (recipient == emailTemplateArray[dict]["audience"] && formType == emailTemplateArray[dict]["formType"] && !appendedItems.includes(value)) {
      appendedItems.push(value);
      $("#action").append('<option value="' + value + '">' + value + '</option>');
    }
  }
  $("#action").selectpicker("refresh");
  $("#subject").prop("disabled", true);
}

function populatePurpose() {
  // This function will begin by refreshing the 'Purpose' select picker everytime,
  // in order to correctly update it everytime. The function then checks what
  // recipient was choosen from the select picker, and queries all the purposes from
  // the database that correspond to that recipient, and finally appends the purposes
  // into the 'Purpose' selectpicker.
  $("#subject").prop("disabled", false);
  $("#subject").empty()
  $("#subject").selectpicker("refresh")
  $("#subject").val("Subject")
  CKEDITOR.instances["editor1"].setData('')
  let recipient = $("#recipient").val()
  let formType = $("#formType").val()
  let action = $("#action").val()
  fieldsDict = {recipient: recipient,
                formType: formType,
                action: action};
  fieldsDictSTR = JSON.stringify(fieldsDict);
  $.ajax({
    url: "/admin/emailTemplates/getPurpose/" + fieldsDictSTR,
    dataType: "json",
    success: function(response){
      let value;
      value = response[0]["Subject"]
      $("#subject").selectpicker("refresh");
      $('#subject').val(value);
      populateEmailTemplate();
    }
  })
}

function populateEmailTemplate() {
  // This method starts by clearing the subject and the body on the UI. Once that
  // is completed, this method will call the purpose. The purpose is used to pull
  // the subject and body from the appropriate template in the database and
  // fill them in the purpose selectpicker and the CKEditor body.
  CKEDITOR.instances["editor1"].setData('');
  let purpose = $("#purpose").val();
  fieldsDict = {"action": $("#action").val(),
                "formType":$("#formType").val(),
                "recipient":$("#recipient").val()
               };
  fieldsDictSTR = JSON.stringify(fieldsDict);
  $.ajax({
    url: "/admin/emailTemplates/getEmail/" + fieldsDictSTR,
    dataType: "json",
    success: function(response){
      let body = response["emailBody"]
      let subject = response["emailSubject"]
      CKEDITOR.instances["editor1"].insertHtml(body);
      // $("#subject").val(subject)
    }
  })
}

function postEmailTemplate() {
  // This method will check what purpose is selected and what is currently
  // selected in the CKEditor body. Then on an AJAX call we send that to the
  // database to override the current body of the email template that was
  // selected. On success, we reload the page and give a python success flash message.
  let body = CKEDITOR.instances.editor1.getData();
  let purpose = $("#subject").val();
  let action = $("#action").val();
  let formType = $("#formType").val();
  let recipient = $("#recipient").val();
  $.ajax({
    url: "/admin/emailTemplates/postEmail",
    data: { 'body': body, 'purpose': purpose, 'action': action, 'formType': formType, 'recipient': recipient},
    dataType: 'json',
    type: 'POST',
    success: function(response){
      location.reload()
    }
  })
}

function discard() {
  // This method first checks to see if a purpose was selected or not. If no
  // purpose was selected, it will flash an error message saying there were no
  // changes to be discarded. If a purpose was selected, the method will clear all
  // three selectpickers and the CKEditor body.
  if ( !$("#subject").val() && !$("#editor1").val() ) {
    msg = "There are no changes to be discarded.";
    category = "danger";
  } else {
    $("#recipient").val('default').selectpicker("refresh")
    $("#formType").empty()
    $("#formType").val('default').selectpicker("refresh")
    $("#action").empty()
    $("#action").val('default').selectpicker("refresh")
    $("#subject").empty()
    $("#subject").val('').selectpicker("refresh")
    CKEDITOR.instances["editor1"].setData('')
    msg = "The email template changes have been discarded.";
    category = "info";
  }
  $("#flash_container").prepend('<div class="alert alert-'+ category +'" role="alert" id="flasher">'+msg+'</div>');
  $("#flasher").delay(3000).fadeOut();
}

function saveChanges() {
  // This method checks to see if a purpose was selected or not. If no purpose
  // was selected, it will flash an error message saying there were no changes
  // to be discarded. If a purpose was selected, the method will call a modal that
  // will ask the user if they are sure they want to save their changes.
  if ( !$("#subject").val() ) {
    msg = "There are no changes to be saved.";
    category = "danger";
    $("#flash_container").prepend('<div class="alert alert-'+ category +'" role="alert" id="flasher">'+msg+'</div>');
    $("#flasher").delay(3000).fadeOut();
  } else {
    $("#modal").modal("show");
  }
}
