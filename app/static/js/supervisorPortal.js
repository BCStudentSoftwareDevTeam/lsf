$(document).ready(function(){
  if ((document.cookie).includes("lsfSearchResults=")) {
    runFormSearchQuery(Cookies.get('lsfSearchResults'));
    setFormSearchValues()
  } else {
      $('#formSearchTable').hide();
      $("#download").prop('disabled', true);
      $('#collapseSearch').collapse(false)
  }
  $('#formSearchButton').on('click', function(){
    runFormSearchQuery(cookieData='');
    setFormSearchValues()

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
    $("input:checkbox").removeAttr("checked");
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
  $("input:checkbox").removeAttr("checked");
  runFormSearchQuery(cookieData='', "mySupervisees");
  setFormSearchValues()
});
$('#evaluationsMissing').on('click', function(){
  $("input:checkbox").removeAttr("checked");
  runFormSearchQuery(cookieData='', "missingEvals");
  setFormSearchValues()
});
$('#superviseesPendingForms').on('click', function(){
  $("input:checkbox").removeAttr("checked");
  runFormSearchQuery(cookieData='', "pendingForms");
  setFormSearchValues()
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

  $("input:checkbox[name='formStatus']:checked").each(function(){
      formStatusList.push($(this).val());
  });

  $("input:checkbox[name='formType']:checked").each(function(){
      formTypeList.push($(this).val());
  });

  $("input:checkbox[name='evaluations']:checked").each(function(){
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
      formStatusList = ["Approved", "Approved Reluctantly"]
      formType  = []
      evaluationList = ["evalMissing", "evalMidyearMissing"]
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

  if (cookieData.length) {
      data = cookieData
  }

  var inAnHour = new Date(new Date().getTime() + 60 * 60 * 1000);
  Cookies.set('lsfSearchResults', data, {expires: inAnHour})

  createDataTable()
}

function createDataTable(){
  data = Cookies.get('lsfSearchResults')
  
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
      
function setFormSearchValues(){
  cookieData = JSON.parse(Cookies.get('lsfSearchResults'))

  console.log(cookieData)
  if (cookieData.termCode == "currentTerm"){
    $("#termSelect").selectpicker("val", g_currentTerm);
  } else {
    $("#termSelect").selectpicker("val", cookieData.termCode);
  }
  if (cookieData.supervisorID == "currentUser"){
    $("#supervisorSelect").selectpicker("val", g_currentUser);
  } else {
    $("#supervisorSelect").selectpicker("val", cookieData.supervisorID);
  }  
  $("#departmentSelect").selectpicker("val", cookieData.departmentID);
  $("#studentSelect").selectpicker("val", cookieData.studentID);

  $(cookieData.evaluations).each(function(i, value){
    $(`input:checkbox[value='${value}']`).prop('checked', true);
  })
  $(cookieData.formType).each(function(i, value){
    $(`input:checkbox[value='${value}']`).prop('checked', true);
  })
  $(cookieData.formStatus).each(function(i, value){
    $(`input:checkbox[value='${value}']`).prop('checked', true);
  })
}

