function addSupervisorToDepartment(supervisorID, departmentID) {
    $.ajax({
      method: "POST",
      url: `/supervisorPortal/addUserToDept`,
      data: {"supervisorID": supervisorID, "departmentID": departmentID},
      success: function(response) {
        if (response == "True") {
          msgFlash("Supervisor has been added to department.", 'success')
          clearDropdown()
        } else {
          msgFlash("Supervisor is already a member of this department.", "warning")
          clearDropdown()
        }
      },
      error: function() {
        msgFlash("Failed to add supervisor, please try again.", "fail")
        clearDropdown()
      },
    })
}

function clearDropdown(){
    $('select.selectpicker').each(function() {
      $(`#${this.id} option:eq(0)`).prop("selected", true);
      $(`#${this.id}`).selectpicker("refresh");
    });
};