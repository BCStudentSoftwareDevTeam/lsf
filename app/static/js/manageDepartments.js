// Opens collapse menu for this page
$("#admin").collapse("show");

$(document).ready( function(){
    x = $('#departmentsTable');
    //console.log(x);
    x.DataTable({
        pageLength: 25
    });
    $('#departmentsTable').on('draw.dt', function() {
      $('.supervisorDeptModal').on('click', function(){
        console.log(this.id)
        getSupervisorDepartments(this.id)
        console.log("Beans")
        $('#manageDepartmentSupervisorModal').modal('show')
      })
    })
    $('#manageDepartmentSupervisorModal').on('blur', emptyManageDepartmentSupervisorModal)
    $('#closeManageDepartmentSupervisorModal').on('click', emptyManageDepartmentSupervisorModal)
});

function emptyManageDepartmentSupervisorModal() {
  $('#manageDepartmentSupervisorModal').modal('hide')
  $('.changing-content').empty()
}

function getSupervisorDepartments(departmentID) {
  $.ajax({
    method: "GET",
    url: `/admin/manageDepartments/${departmentID}`,
    success: function(departmentsAndSupervisors) {
      let currentDepartment=departmentsAndSupervisors[0]
      let supervisors=departmentsAndSupervisors[1]
      $('#manageSupervisorContent .modal-header .changing-content').append("<p>"+currentDepartment['DEPT_NAME']+"</p>")
      for (let i=0; i<supervisors.length; i++) {
        $('#manageSupervisorContent .modal-body .changing-content').append(`<p>${supervisors[i]['ID']} ${supervisors[i]['preferred_name']} ${supervisors[i]['LAST_NAME']}</p>`)
      }
    }
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
