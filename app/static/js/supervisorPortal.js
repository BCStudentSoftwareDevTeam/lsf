$(document).ready(function(){
  if ((document.cookie).includes("lsfSearchResults=")) {
    cookieStr = Cookies.get('lsfSearchResults')
    createDataTable(cookieStr)
    setFormSearchValues(JSON.parse(cookieStr))

  } else {
      $('#formSearchTable').hide();
      $("#download").prop('disabled', true);
      $('#collapseSearch').collapse(false)
  }

  $('#formSearchButton').on('click', function(){
    runFormSearchQuery();

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
  runFormSearchQuery("mySupervisees");
});
$('#evaluationsMissing').on('click', function(){
  $("input:checkbox").removeAttr("checked");
  runFormSearchQuery("missingEvals");
});
$('#superviseesPendingForms').on('click', function(){
  $("input:checkbox").removeAttr("checked");
  runFormSearchQuery("pendingForms");
});
$('#currentTerm').on('click', function(){
  runFormSearchQuery("currentTerm");
});
});

function clearDropdown(){
  $('select.selectpicker').each(function() {
    $(`#${this.id} option:eq(0)`).prop("selected", true);
    $(`#${this.id}`).selectpicker("refresh");
  });
};

function runFormSearchQuery(button) {

  let termCode, departmentID, supervisorID, studentID;
  let formStatusList = [];
  let formTypeList = [];
  let evaluationList = [];

  switch(button) {
      case "mySupervisees":
          termCode = "currentTerm"
          departmentID = ""
          supervisorID = "currentUser"
          studentID = ""
          formStatusList = []
          formType  = []
          evaluationList = []
          break;

      case "missingEvals":
          termCode = "currentTerm"
          departmentID = ""
          supervisorID = "currentUser"
          studentID = ""
          formStatusList = ["Approved", "Approved Reluctantly"]
          formType  = []
          evaluationList = ["evalMissing", "evalMidyearMissing"]
          break;

      case "pendingForms":
          termCode = "currentTerm"
          departmentID = ""
          supervisorID = "currentUser"
          studentID = ""
          formStatusList = ["Pending"]
          formType  = []
          evaluationList = []
          break;

      case "currentTerm":
          termCode = "currentTerm"
          departmentID = ""
          supervisorID = ""
          studentID = ""
          formStatusList = []
          formType  = []
          evaluationList = []
          break;

      default:
          termCode = $("#termSelect").val();
          departmentID = $("#departmentSelect").val();
          supervisorID = $("#supervisorSelect").val();
          studentID = $("#studentSelect").val();
          formStatusList = $("input:checkbox[name='formStatus']:checked").map((i,el) => el.value).get();
          formTypeList = $("input:checkbox[name='formType']:checked").map((i,el) => el.value).get();
          evaluationList = $("input:checkbox[name='evaluations']:checked").map((i,el) => el.value).get();      
  }
  
  queryDict = {'termCode': termCode,
               'departmentID': departmentID,
               'supervisorID': supervisorID,
               'studentID': studentID,
               'formStatus': formStatusList,
               'formType': formTypeList,
               'evaluations': evaluationList
             };

  setFormSearchValues(queryDict)
  data = JSON.stringify(queryDict)

  var inAnHour = new Date(new Date().getTime() + 60 * 60 * 1000);
  Cookies.set('lsfSearchResults', data, {expires: inAnHour})

  createDataTable(data)
}

function createDataTable(data){
  
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
      
function setFormSearchValues(searchDict){
  
  if (searchDict.termCode == "currentTerm"){
    $("#termSelect").selectpicker("val", g_currentTerm);
  } else {
    $("#termSelect").selectpicker("val", searchDict.termCode);
  }
  if (searchDict.supervisorID == "currentUser"){
    $("#supervisorSelect").selectpicker("val", g_currentUser);
  } else {
    $("#supervisorSelect").selectpicker("val", searchDict.supervisorID);
  }  
  $("#departmentSelect").selectpicker("val", searchDict.departmentID);
  $("#studentSelect").selectpicker("val", searchDict.studentID);

  $(searchDict.evaluations).each(function(i, value){
    $(`input:checkbox[value='${value}']`).prop('checked', true);
  })
  $(searchDict.formType).each(function(i, value){
    $(`input:checkbox[value='${value}']`).prop('checked', true);
  })
  $(searchDict.formStatus).each(function(i, value){
    $(`input:checkbox[value='${value}']`).prop('checked', true);
  })
}

