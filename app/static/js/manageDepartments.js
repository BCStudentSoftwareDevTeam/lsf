// Opens collapse menu for this page
$("#admin").collapse("show");

$(document).ready( function(){
    activeDepartmentsTable = $('#activeDepartmentsTable');
    activeDepartmentsTable.DataTable({
        pageLength: 25
    });

    
    inactiveDepartmentsTable = $('#inactiveDepartmentsTable');
    inactiveDepartmentsTable.DataTable({
      pageLength: 25
    });
    $("#inactiveTable").hide();

    $("#activeTab").on("click", function() {
      $("#activeTab").addClass("active");
      $("#activeTable").show();
      $("#inactiveTab").removeClass("active");
      $("#inactiveTable").hide();
    })

    $("#inactiveTab").on("click", function() {
      $("#activeTab").removeClass("active");
      $("#activeTable").hide();
      $("#inactiveTab").addClass("active");
      $("#inactiveTable").show();
    })
    
    attachModalToDepartment()
    $('.deptTable').on('draw.dt', function() {
      attachModalToDepartment()
    })
    $('#manageDepartmentSupervisorModal').on('hidden.bs.modal', function() {
      clearDropdowns()
    })
});


function attachModalToDepartment() {
    $('.supervisorDeptModal').off('click')
    $('.supervisorDeptModal').on('click', function() {
      $('#manageSupervisorContent .modal-header .department-name')
                .replaceWith(`<h2 class='department-name' id="departmentModalSelect" data-department-id="${this.id}">
                                    ${$(`#${this.id}`).html()}
                              </h2>`)
      getSupervisorsInDepartment(this.id)
    })
}


$("#supervisorModalSelect").on('change', function() {
  let supervisorID = $('#supervisorModalSelect :selected').val()
  let departmentID = $('#departmentModalSelect').data('department-id')
  addSupervisorToDepartment(supervisorID, departmentID, ()=>getSupervisorsInDepartment(departmentID))
  
})

  

function getSupervisorsInDepartment(departmentID) {
    $.ajax({
    method: "GET",
    url: `/admin/manageDepartments/${departmentID}`,
    success: function(departmentsAndSupervisors) {
      let currentDepartment=departmentsAndSupervisors[0]
      let supervisors=departmentsAndSupervisors[1]
      
      let supervisorContent = '<div class="changing-content">'
      for (let i=0; i<supervisors.length; i++) {
        let supervisorFirstName= supervisors[i]['preferred_name'] ? supervisors[i]['preferred_name'] : supervisors[i]['legal_name']
        supervisorContent += (`<span class="row">
                                <div class="col-xs-10">${supervisors[i]['ID']} ${supervisorFirstName} ${supervisors[i]['LAST_NAME']}</div>
                                <div class='btn btn-danger col-auto removeSupervisorFromDepartment' 
                                  data-supervisor="${supervisors[i]['ID']}" 
                                  data-department="${currentDepartment['departmentID']}" 
                                  id="${supervisors[i]['ID']}-${currentDepartment['departmentID']}">Remove</div>
                               </span>`)}
      supervisorContent += ("</div>")
      $('#manageSupervisorContent .modal-body .changing-content').replaceWith(supervisorContent)
      
      $('#manageDepartmentSupervisorModal').modal('show')
      $('.removeSupervisorFromDepartment').on('click', removeSupervisorFromDepartment)
    }
    })
  }

function removeSupervisorFromDepartment () {
  let department = $(`#${this.id}`).data('department')
  let supervisor = $(`#${this.id}`).data('supervisor')
  let data = {"supervisorID": supervisor, "departmentID": department}
  $.ajax({
    method: "POST",
    url: "/admin/manageDepartments/removeSupervisorFromDepartment",
    data: data,
    success: function(response) {
        if (response == "True") {
          msgFlash("Supervisor has been removed from department.", 'success')
          getSupervisorsInDepartment(department)
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
