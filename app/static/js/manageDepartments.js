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

    $('#allocationPreviewButton').on('click', loadAllocationDownloadPreview)
    $('#allocationAcademicYear').on('change', function() {
      $('#allocationDownloadError').prop('hidden', true).text('')
    })
    $('#confirmAllocationDownload').on('click', function() {
      const academicYearCode = $(this).data('academic-year-code')
      if (academicYearCode) {
        window.location.href = `/admin/manageDepartments/allocations/download/${academicYearCode}`
      }
    })
});

function loadAllocationDownloadPreview() {
  const academicYearCode = $('#allocationAcademicYear').val()
  const errorMessage = $('#allocationDownloadError')

  if (!academicYearCode) {
    errorMessage.text('Select an academic year to preview its allocation download.').prop('hidden', false)
    return
  }

  const previewButton = $('#allocationPreviewButton')
  previewButton.prop('disabled', true).text('Loading...')
  errorMessage.prop('hidden', true).text('')

  $.ajax({
    method: 'GET',
    url: `/admin/manageDepartments/allocations/${academicYearCode}`,
    dataType: 'json',
    success: function(response) {
      const rows = $('#allocationDownloadPreviewRows').empty()
      const totals = {
        primary_10: 0,
        primary_12: 0,
        primary_15: 0,
        primary_20: 0,
        secondary_5: 0,
        secondary_10: 0,
        break_hours: 0
      }

      response.allocations.forEach(function(allocation) {
        const values = [
          allocation.department,
          allocation.primary_10,
          allocation.primary_12,
          allocation.primary_15,
          allocation.primary_20,
          allocation.secondary_5,
          allocation.secondary_10,
          allocation.break_hours
        ]
        const row = $('<tr>')
        values.forEach(function(value) {
          row.append($('<td>').text(value))
        })
        rows.append(row)

        Object.keys(totals).forEach(function(key) {
          totals[key] += Number(allocation[key]) || 0
        })
      })

      const totalPrimaries = totals.primary_10 + totals.primary_12 + totals.primary_15 + totals.primary_20
      const totalSecondaries = totals.secondary_5 + totals.secondary_10
      $('#allocationDownloadSummary').text(
        `${response.academicYear}: ${response.allocations.length} department allocation(s), ` +
        `${totalPrimaries} primary positions, ${totalSecondaries} secondary positions, and ` +
        `${totals.break_hours} break hours. Preview the stored final allocations below.`
      )
      $('#confirmAllocationDownload').data('academic-year-code', academicYearCode)
      $('#allocationDownloadModal').one('hidden.bs.modal', function() {
        $('#allocationDownloadPreviewModal').modal('show')
      }).modal('hide')
    },
    error: function(xhr) {
      const message = xhr.responseJSON && xhr.responseJSON.error
        ? xhr.responseJSON.error
        : 'Unable to load the allocation preview. Please try again.'
      errorMessage.text(message).prop('hidden', false)
    },
    complete: function() {
      previewButton.prop('disabled', false).text('Preview Download')
    }
  })
}


function attachModalToDepartment() {
    $('.deptTable .departmentName').off('click')
    $('.deptTable .departmentName').on('click', function() {
      $('#manageSupervisorContent .modal-header .department-name')
                .replaceWith(`<h2 class='department-name' id="departmentModalSelect" data-department-id="${this.id}">
                                    ${$(`#${this.id}`).html()}
                              </h2>`)
      showSupervisorsInDepartment(this.id)
    })
}


$("#supervisorModalSelect").on('change', function() {
  let supervisorID = $('#supervisorModalSelect :selected').val()
  let departmentID = $('#departmentModalSelect').data('department-id')
  addSupervisorToDepartment(supervisorID, departmentID, ()=>showSupervisorsInDepartment(departmentID))
  
})

  

function showSupervisorsInDepartment(departmentID) {
    $.ajax({
    method: "GET",
    url: `/admin/manageDepartments/${departmentID}`,
    success: function(supervisors) {   
      let supervisorContent = '<div class="changing-content">'
      for (let i=0; i<supervisors.length; i++) {
        let supervisorFirstName = supervisors[i]['preferred_name'] ? supervisors[i]['preferred_name'] : supervisors[i]['legal_name']
        supervisorContent += (`<span class="row">
                                <div class="col-xs-10">${supervisors[i]['ID']} ${supervisorFirstName} ${supervisors[i]['LAST_NAME']}</div>
                                <div class='btn btn-danger col-auto removeSupervisorFromDepartment' 
                                  data-supervisor="${supervisors[i]['ID']}" 
                                  data-department="${departmentID}" 
                                  id="${supervisors[i]['ID']}-${departmentID}">Remove</div>
                               </span>`)}
      supervisorContent += ("</div>")
      $('#manageSupervisorContent .modal-body .changing-content').replaceWith(supervisorContent)
      
      $('#manageDepartmentSupervisorModal').modal('show')
      $('.removeSupervisorFromDepartment').on('click', removeSupervisorFromDepartment)
    }
    })
  }

function removeSupervisorFromDepartment () {
  let departmentID = $(`#${this.id}`).data('department')
  let supervisorID = $(`#${this.id}`).data('supervisor')
  let data = {"supervisorID": supervisorID, "departmentID": departmentID}
  $.ajax({
    method: "POST",
    url: "/admin/manageDepartments/removeSupervisorFromDepartment",
    data: data,
    success: function(response) {
        if (response == "True") {
          msgFlash("Supervisor has been removed from department.", 'success')
          showSupervisorsInDepartment(departmentID)
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
