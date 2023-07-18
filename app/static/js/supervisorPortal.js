$(document).ready(function(){
  if ((document.cookie).includes("lsfSearchResults=")) {
       console.log(document.cookie)
        runFormSearchQuery(Cookies.get('lsfSearchResults'));
  } else {
      $('#formSearchTable').hide();
      $("#download").prop('disabled', true);
      $('#collapseSearch').collapse(false)
  }
  $('#formSearchButton').on('click', function(){
    runFormSearchQuery(cookieData='');
  });
  $('#addUserToDept').on('click', function() {
      $("#addSupervisorToDeptModal").modal("show");
  })

  $('#addUser').on('click', function() {
      let supervisor = $('#supervisorModalSelect :selected').val()
      let department = $('#departmentModalSelect :selected').val()
      let data = {"supervisor": supervisor, "department": department}
      $.ajax({
        method: "POST",
        url: "/supervisorPortal/addUserToDept",
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
  })
  $('#clearSelectionsButton').on('click', function(){
    $("input:radio:checked").removeAttr("checked");
    clearDropdown()
    });
    
  $( function() {
    $( "#formSearchAccordion" ).accordion({
      collapsible: true
    });
  });
  $(function() {
    $( "#formSearchAccordion" ).accordion();
  	$("#formSearchAccordion .ui-accordion-header").css({fontSize: 20});// width of the box content area
});
// listening for preset button clicks.
$('#mySupervisees').on('click', function(){
  runFormSearchQuery(cookieData='', "mySupervisees");
});
$('#evaluationsMissing').on('click', function(){
  runFormSearchQuery(cookieData='', "missingEvals");
});
$('#superviseesPendingForms').on('click', function(){
  runFormSearchQuery(cookieData='', "pendingForms");
});
$('#currentTerm').on('click', function(){
  runFormSearchQuery(cookieData='', "currentTerm");
});
});

function clearDropdown(){
  $('select.selectpicker').each(function() {
    $(`#${this.id} option:eq(0)`).prop("selected", true);
    $(`#${this.id}`).selectpicker("refresh");
  });
};

function runFormSearchQuery(cookieData='', button) {

  var termCode = $("#termSelect").val();
  var departmentID = $("#departmentSelect").val();
  var supervisorID = $("#supervisorSelect").val();
  var studentID = $("#studentSelect").val();
  var formStatusList = [];
  var formTypeList = [];
  var evaluationList = [];

  $("input:radio[name='formStatus']:checked").each(function(){
      formStatusList.push($(this).val());
  });

  $("input:radio[name='formType']:checked").each(function(){
      formTypeList.push($(this).val());
  });

  $("input:radio[name='evaluations']:checked").each(function(){
      evaluationList.push($(this).val());
  });
  if (button) {
    if (button=="mySupervisees") {
      termCode = "currentTerm"
      departmentID = ""
      supervisorID = "currentUser"
      studentID = ""
      formStatusList = []
      formType  = []
      evaluationList = []
    } else if (button=="missingEvals") {
      termCode = "currentTerm"
      departmentID = ""
      supervisorID = "currentUser"
      studentID = ""
      formStatusList = []
      formType  = []
      evaluationList = ["allEvalMissing"]
    } else if (button=="pendingForms") {
      termCode = "currentTerm"
      departmentID = ""
      supervisorID = "currentUser"
      studentID = ""
      formStatusList = ["Pending"]
      formType  = []
      evaluationList = []
    } else if (button=="currentTerm") {
      termCode = "currentTerm"
      departmentID = ""
      supervisorID = ""
      studentID = ""
      formStatusList = []
      formType  = []
      evaluationList = []
    }
  }
  queryDict = {'termCode': termCode,
               'departmentID': departmentID,
               'supervisorID': supervisorID,
               'studentID': studentID,
               'formStatus': formStatusList,
               'formType': formTypeList,
               'evaluations': evaluationList
             };
  data = JSON.stringify(queryDict)
  console.log(data)
  if (cookieData.length) {
      data = cookieData
      console.log(data)
  }
  let now = new Date();
  now.setMinutes(now.getMinutes() + 15);
  // var searchCookie = document.cookie = "lsfSearchResults="+data +"; expires=" + now.toUTCString() +";"
  Cookies.set('lsfSearchResults', data)
  if (evaluationList.length > 0 && termCode == "") {
    $("#flash_container").html('<div class="alert alert-danger" role="alert" id="flasher">Term must be selected with evaluation status.</div>');
    $("#flasher").delay(5000).fadeOut();
  }
  else if (evaluationList.length == 0 && formStatusList.length == 0 && formTypeList.length == 0 && termCode == "" && departmentID == "" && supervisorID == "" && studentID == "" && cookieData.length == 0){
    $("#flash_container").html('<div class="alert alert-danger" role="alert" id="flasher">At least one field must be selected.</div>');
    $("#flasher").delay(3000).fadeOut();
  } else {
    $("#formSearchAccordion").accordion({ collapsible: true, active: false});
    $("#download").prop('disabled', false);
    $('#formSearchTable').show();
    var formSearchInit = $('#formSearchTable').DataTable({
          responsive: true,
          destroy: true,
          searching: false,
          processing: true,
          serverSide: true,
          paging: true,
          lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
          pageLength: 25,
          aaSorting: [[0, 'desc']],
          columnDefs: [{
            targets: -1,
            orderable: false,
          }],
          ajax: {
              url: "/",
              type: "POST",
              data: {'data': data},
              dataSrc: "data",
        }
    });
  }
}
