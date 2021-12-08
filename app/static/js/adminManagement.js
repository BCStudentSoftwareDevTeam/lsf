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
};


function modal(button) {
  if(button == "add" && $("#addlaborAdmin").val() != "") {
    $("h2").html("Labor Administrators");
    $("p").html("Are you sure you want to add " + $("#addlaborAdmin option:selected").text() + " as a Labor Administrator?");
    document.getElementById("submitModal").setAttribute("name", "add");
    document.getElementById("submitModal").setAttribute("value", "add");
    $("#modal").modal("show");
  }
  else if(button == "add1" && $("#addFinAidAdmin").val() != "") {
    $("h2").html("Financial Aid Administrators");
    $("p").html("Are you sure you want to add " + $("#addFinAidAdmin option:selected").text() + " as a Financial Aid Administrator?");
    document.getElementById("submitModal").setAttribute("name", "addAid");
    document.getElementById("submitModal").setAttribute("value", "addAid");
    $("#modal").modal("show");
  }
  else if(button == "add2" && $("#addSaasAdmin").val() != "") {
    $("h2").html("SAAS Administrators");
    $("p").html("Are you sure you want to add " + $("#addSaasAdmin option:selected").text() + " as a SAAS Administrator?");
    document.getElementById("submitModal").setAttribute("name", "addSaas");
    document.getElementById("submitModal").setAttribute("value", "addSaas");
    $("#modal").modal("show");
  }
  else if(button == "remove" && $("#removelaborAdmin").val() != "") {
    $("h2").html("Labor Administrators");
    $("p").html("Are you sure you want to remove " + $("#removelaborAdmin option:selected").text() + " as a Labor Administrator?");
    document.getElementById("submitModal").setAttribute("name", "remove");
    document.getElementById("submitModal").setAttribute("value", "remove");
    $("#modal").modal("show");
  }
  else if(button == "remove1" && $("#removeFinAidAdmin").val() != "") {
    $("h2").html("Financial Aid Administrators");
    $("p").html("Are you sure you want to remove " + $("#removeFinAidAdmin option:selected").text() + " as a Financial Aid Administrator?");
    document.getElementById("submitModal").setAttribute("name", "removeAid");
    document.getElementById("submitModal").setAttribute("value", "removeAid");
    $("#modal").modal("show");
  }
  else if(button == "remove2" && $("#removeSaasAdmin").val() != "") {
    $("h2").html("SAAS Administrators");
    $("p").html("Are you sure you want to remove " + $("#removeSaasAdmin option:selected").text() + " as a SAAS Administrator?");
    document.getElementById("submitModal").setAttribute("name", "removeSaas");
    document.getElementById("submitModal").setAttribute("value", "removeSaas");
    $("#modal").modal("show");
  }
  else {
    category = "danger"
    msg = "Please select a user.";
    $("#flash_container").html('<div class="alert alert-'+ category +'" role="alert" id="flasher">'+msg+'</div>')
    $("#flasher").delay(3000).fadeOut()
      }
};
