// Opens collapse menu for this page
$("#admin").collapse("show");

$(document).ready( function(){
    x = $('#departmentsTable');
    //console.log(x);
    x.DataTable({
        pageLength: 25
    });

    attachModalsToDepartment()
    $('#departmentsTable').on('draw.dt', attachModalsToDepartment)
    $('#manageDepartmentSupervisorModal').on('hidden.bs.modal', function() {
      $('#manageDepartmentSupervisorModal').modal('hide')
      $('.changing-content').empty()  
    })
    $('#manageDepartmentSupervisorModal').on('shown.bs.modal', function() {
      $('.removeSupervisorFromDepartment').on('click', removeSupervisorFromDepartment)
    })
});


function updateModal(departmentID) {
  $('.changing-content').empty() 
  getSupervisorDepartments(departmentID)
}

function attachModalsToDepartment() {
    $('.supervisorDeptModal').on('click', function() {
      getSupervisorDepartments(this.id)
    })
}



// Stole from Finn's work review to ensure functionality
$("#addSupervisorsToDepartmentSubmit").on('click', function() {
  let supervisor = $('#supervisorModalSelect :selected').val()
  let department = $('#departmentModalSelect').data('department-id')
  let data = {"supervisor": supervisor, "department": department}
  addSupervisorToDepartment(data)
})



function getSupervisorDepartments(departmentID) {
    $.ajax({
    method: "GET",
    url: `/admin/manageDepartments/${departmentID}`,
    success: function(departmentsAndSupervisors) {
      let currentDepartment=departmentsAndSupervisors[0]
      let supervisors=departmentsAndSupervisors[1]
      $('#manageSupervisorContent .modal-header .changing-content')
            .append(`<h2 id="departmentModalSelect" data-department-id="${currentDepartment['departmentID']}">
                          ${currentDepartment['DEPT_NAME']}
                     </h2>`)
      for (let i=0; i<supervisors.length; i++) {
        $('#manageSupervisorContent .modal-body .changing-content')
              .append(`<div class="row form-group">
                        <div class="col">${supervisors[i]['ID']} ${supervisors[i]['preferred_name']} ${supervisors[i]['LAST_NAME']}</div>
                        <div class='btn btn-danger col removeSupervisorFromDepartment' 
                          data-supervisor="${supervisors[i]['ID']}" 
                          data-department="${currentDepartment['departmentID']}" 
                          id="${supervisors[i]['ID']}-${currentDepartment['departmentID']}">Remove</div>
                      </div>`)}
      $('#manageDepartmentSupervisorModal').modal('show')
    }
    })
  }

function removeSupervisorFromDepartment () {
  let department = $(`#${this.id}`).data('department')
  let supervisor = $(`#${this.id}`).data('supervisor')
  let data = {"supervisor": supervisor, "department": department}
  $.ajax({
    method: "POST",
    url: "/admin/manageDepartments/removeSupervisorFromDepartment",
    data: data,
    success: function(response) {
        if (response == "True") {
          msgFlash("Supervisor has been removed from department.", 'success')
          updateModal(department)
        } else {
          msgFlash("Supervisor is not a member of this department.", "warning")
        }
      },
      error: function() {
        msgFlash("Failed to remove supervisor, please try again.", "fail")
      },
    })
}

function status(department, dept_name) {
/*
 POSTs the compliance status change for the department. Updates UI with correct button and feedback to user.
 PARAMS:
    int department: department ID
    str dept_name: Name of the department

 RETURNS: None
*/
  $.ajax({
    method: "POST",
    url: "/admin/complianceStatus",
    dataType: "json",
    contentType: "application/json",
    data: JSON.stringify({"deptName": department}),
    processData: false,
    success: function(response) {
//      console.log(response);
      if(response["Success"]) {
        category = "info"
        var departmentID = $("#dept_btn_" + department);
        //console.log(departmentID);
        if ($(departmentID).hasClass("btn-success")){
          $(departmentID).removeClass("btn-success");
          $(departmentID).addClass("btn-danger");
          $(departmentID).text("Not in Compliance");
          msg = "The " + dept_name +" department's compliance status was changed to 'Not in compliance'.";
          $("#dept_" + department).attr("data-order", -1);
          category = "danger";
        }
        else {
          $(departmentID).removeClass("btn-danger");
          $(departmentID).addClass("btn-success");
          $(departmentID).text("In Compliance");
          msg = "The " + dept_name +" department's compliance status was changed to 'In compliance'.";
          $("#dept_" + department).attr("data-order", 1);
          category = "success";
        }

        $("#flash_container").html('<div class="alert alert-'+ category +'" role="alert" id="flasher">'+msg+'</div>');
        $("#flasher").delay(3000).fadeOut();
//        $('#departmentsTable').DataTable().ajax.reload();     #FIXME the table doesn't sort correctly after the ajax response.
      }
    }
  })
};
