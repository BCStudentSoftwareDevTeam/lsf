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
});

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
