function msgFlash(flash_message, status){
    var category = (status === "success") ? "success" : ((status === "fail") ? "danger" : "warning");
    $("#flash_container").prepend('<div class="alert alert-'+ category +'" role="alert" id="flasher">'+flash_message+'</div>');
    $("#flasher").delay(5000).fadeOut();
}

function addSupervisorToDepartment(data) {
    $.ajax({
      method: "POST",
      url: `/supervisorPortal/addUserToDept`,
      data: data,
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