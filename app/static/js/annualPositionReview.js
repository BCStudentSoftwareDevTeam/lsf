function submitAnnualPositionReview() {
/*
 POSTs the Annual Position Review request for the currently selected academic year.
 Sends a review request email to every active department's Labor Coordinators and
 supervisors, then shows a success/failure flash message.

 RETURNS: None
*/
  var academicYear = $('[data-target="#annualPositionModal"]').data('academic-year');

  $.ajax({
    method: "POST",
    url: "/admin/manageDepartments/annualPositionReview",
    dataType: "json",
    contentType: "application/json",
    data: JSON.stringify({"academicYear": academicYear}),
    success: function(response) {
      $("#annualPositionModal").modal("hide");

      if (response["Success"]) {
        flashMessage("success", "Position review requests sent to " + response["sentCount"] + " of " + response["departmentCount"] + " departments.");
      } else {
        flashMessage("danger", "Something went wrong sending the Annual Position Review requests.");
      }
    },
    error: function(jqXHR) {
      // Covers cases success: never sees - a 403 (not a labor admin), a 500,
      // or the request failing outright. Leaves the modal open so the admin
      // can retry instead of silently doing nothing.
      var msg = jqXHR.status === 403
        ? "You don't have permission to send Annual Position Review requests."
        : "Something went wrong sending the Annual Position Review requests.";
      flashMessage("danger", msg);
    }
  })
}

function flashMessage(category, msg) {
  $("#flash_container").html('<div class="alert alert-'+ category +'" role="alert" id="flasher">'+msg+'</div>');
  $("#flasher").delay(3000).fadeOut();
}
