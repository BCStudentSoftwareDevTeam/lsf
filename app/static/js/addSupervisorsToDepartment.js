function addSupervisorToDepartment(supervisorID, departmentID, callback=None) {
    return $.ajax({
      method: "POST",
      url: `/supervisorPortal/addUserToDept`,
      data: {"supervisorID": supervisorID, "departmentID": departmentID},
      success: function(response) {
        if (response == "True") {
          msgFlash("Supervisor has been added to department.", 'success')
          clearDropdowns()
        } else {
          msgFlash("Supervisor is already a member of this department.", "warning")
          clearDropdowns()
        }
        if (callback){
          callback()
        }
      },
      error: function() {
        msgFlash("Failed to add supervisor, please try again.", "fail")
        clearDropdowns()
      },
    })

}

function clearDropdowns(){
    $('select.selectpicker').each(function() {
      $(`#${this.id} option:eq(0)`).prop("selected", true);
      $(`#${this.id}`).selectpicker("refresh");
    });
};