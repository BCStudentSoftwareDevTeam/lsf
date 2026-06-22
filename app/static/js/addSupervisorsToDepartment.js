function addSupervisorToDepartment(supervisorID, departmentID, supervisor_FirstName, supervisor_LastName, callback=() => {}) {
  let supervisorfirstName = supervisor_FirstName
  let supervisorLastName = supervisor_LastName
  console.log("Names  ",supervisorfirstName, supervisorLastName)

    return $.ajax({
      method: "POST",
      url: `/supervisorPortal/addUserToDept`,
      data: {"supervisorID": supervisorID, "departmentID": departmentID},
      success: function(response) {
        if (response == "True") {
          msgFlash(`Supervisor ${supervisorfirstName} ${supervisorLastName} (${supervisorID}) has been added to the department.`, "success")
          clearDropdowns()
        } else {
          msgFlash(`Supervisor ${supervisorfirstName} ${supervisorLastName} (${supervisorID}) is already a member of this department.`, "warning")
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