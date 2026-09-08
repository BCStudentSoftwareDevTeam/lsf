function submitAnnualPositionReview(button) {
/*
 POSTs the Annual Position Review request for the currently selected academic year.
 Sends a review request email to every active department's Labor Coordinators and
 supervisors, then shows a success/failure flash message.

 RETURNS: None
*/
  var academicYear = $('[data-target="#annualPositionModal"]').data('academic-year');

  // Disable immediately so a double-click can't fire this request twice -
  // PositionHistory dedupes the request record, but the emails would still go out
  // more than once. Re-enabled in complete regardless of outcome so a retry
  // after a failure is possible without reloading the page.
  $(button).prop("disabled", true);

  $.ajax({
    method: "POST",
    url: "/admin/manageDepartments/annualPositionReview",
    dataType: "json",
    contentType: "application/json",
    data: JSON.stringify({"academicYear": academicYear}),
    success: function(response) {
      $("#annualPositionModal").modal("hide");

      if (response["Success"]) {
        msgFlash("Position review requests sent to " + response["sentCount"] + " of " + response["departmentCount"] + " departments.", "success");
      } else {
        var msg = response["message"] || ("Requests sent to " + response["sentCount"] + " of " + response["departmentCount"] + " departments, but some requests failed.");
        msgFlash(msg, "fail");
      }
    },
    error: function(jqXHR) {
      // Covers cases success: never sees - a 403 (not a labor admin), a 500,
      // or the request failing outright. Leaves the modal open so the admin
      // can retry instead of silently doing nothing.
      var payload = jqXHR.responseJSON || {};
      var msg = jqXHR.status === 403
        ? "You don't have permission to send Annual Position Review requests."
        : (payload["message"] || "Something went wrong sending the Annual Position Review requests.");
      msgFlash(msg, "fail");
    },
    complete: function() {
      $(button).prop("disabled", false);
    }
  })
}
