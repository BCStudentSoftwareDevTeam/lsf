// Opens collapse menu for this page
$("#admin").collapse("show");

$('#addlaborAdmin').selectpicker('refresh');
$('#addFinAidAdmin').selectpicker('refresh');
$('#addSaasAdmin').selectpicker('refresh');

$("#labor .bs-searchbox input").on("keyup", function(e) {
  liveSearch("addlaborAdmin", e);
});
$("#financialAid .bs-searchbox input").on("keyup", function(e) {
  liveSearch("addFinAidAdmin", e);
});
$("#saas .bs-searchbox input").on("keyup", function(e) {
  liveSearch("addSaasAdmin", e);
});
function liveSearch(selectPickerID, e) {
    let searchData = e.target.value;
    $("#"+ selectPickerID).empty();
    if (searchData.length >= 3) {
      $("#"+ selectPickerID).empty();
      let data = [selectPickerID, searchData]
      data = JSON.stringify(data)
      $.ajax({
        type: "POST",
        url: "/admin/adminSearch",
        datatype: "json",
        data: data,
        contentType: 'application/json',
        success: function(response) {
          for (let key = 0; key < response.length; key++) {
            let username = response[key]['username']
            let firstName = response[key]['firstName']
            let lastName = response[key]['lastName']
            let type = response[key]['type']
            if (type == "Student") {
              $("#"+ selectPickerID).append('<option value="' + username + '" data-subtext="' + username + ' (' + type + ')">' + firstName + ' ' + lastName + '</option>');
            } else {
              $("#"+ selectPickerID).append('<option value="' + username + '" data-subtext="' + username + '">' + firstName + ' ' + lastName + '</option>');
            }
          }
          $("#"+ selectPickerID).selectpicker("refresh");
        }
      });
    }
    else{$("#"+ selectPickerID).selectpicker("refresh");} // clear search list if <3 chars
};

let formToSubmit = null; // store form clicked

function modal(button) {
  // map button IDs to {selectID, formID, header, actionText}
  const config = {
    add:   { select: "#addlaborAdmin",       form: "#laborAdminForm",   header: "Labor Administrators",       action: "add",    noun: "Labor Administrator" },
    add1:  { select: "#addFinAidAdmin",      form: "#finAidAdminForm",  header: "Financial Aid Administrators", action: "add",    noun: "Financial Aid Administrator" },
    add2:  { select: "#addSaasAdmin",        form: "#SAASAdminForm",    header: "SAAS Administrators",        action: "add",    noun: "SAAS Administrator" },
    remove:{ select: "#removelaborAdmin",    form: "#laborAdminForm",   header: "Labor Administrators",       action: "remove", noun: "Labor Administrator" },
    remove1:{ select: "#removeFinAidAdmin",  form: "#finAidAdminForm",  header: "Financial Aid Administrators", action: "remove", noun: "Financial Aid Administrator" },
    remove2:{ select: "#removeSaasAdmin",    form: "#SAASAdminForm",    header: "SAAS Administrators",        action: "remove", noun: "SAAS Administrator" }
  };

  const cfg = config[button];

  const select = $(cfg.select);
  if (!select.val()) {
    // no user selected
    $("#flash_container").html(
      '<div class="alert alert-danger" role="alert" id="flasher">Please select a user.</div>'
    );
    $("#flasher").delay(3000).fadeOut();
    return;
  }

  formToSubmit = $(cfg.form);
  const selectedText = select.find("option:selected").text();
  const message = `Are you sure you want to ${cfg.action} ${selectedText} as a ${cfg.noun}?`;

  // populate modal
  $("#adminModalHeader").html(cfg.header);
  $("#adminModalText").html(message);
  $("#modal").modal("show");
}

$("#submitModal").on("click", function () {
  if (formToSubmit) {
    formToSubmit.submit();
  }
});