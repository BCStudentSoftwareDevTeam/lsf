function addSupervisorToDepartment(supervisorID, departmentID, callback=() => {}) {
    return $.ajax({
      method: "POST",
      url: `/members/add`,
      data: {"supervisorID": supervisorID, "departmentID": departmentID},
      success: function(response) {
        msgFlash(response.message, response.success ? "success" : "warning");
        clearDropdowns();

        if (callback){
          callback();
        }
      },
      error: function(response) {
        let message = "Failed to add supervisor, please try again.";

        if (response.responseJSON && response.responseJSON.message) {
          message = response.responseJSON.message;
        }

        msgFlash(message, "fail");
        clearDropdowns();
      },
    })
}

function clearDropdowns(){
    $('select.selectpicker').each(function() {
      $(`#${this.id} option:eq(0)`).prop("selected", true);
      $(`#${this.id}`).selectpicker("refresh");
    });
};