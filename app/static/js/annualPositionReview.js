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

      var category, msg;
      if (response["Success"]) {
        category = "success";
        msg = "Position review requests sent to " + response["sentCount"] + " of " + response["departmentCount"] + " departments.";
      } else {
        category = "danger";
        msg = "Something went wrong sending the Annual Position Review requests.";
      }

      $("#flash_container").html('<div class="alert alert-'+ category +'" role="alert" id="flasher">'+msg+'</div>');
      $("#flasher").delay(3000).fadeOut();
    }
  })
}
