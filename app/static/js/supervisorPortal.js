$(document).ready(function () {
  if ((document.cookie).includes("lsfSearchResults=")) {
    cookieStr = Cookies.get('lsfSearchResults')
    createDataTable(cookieStr)
    setFormSearchValues(JSON.parse(cookieStr))

  } else {
    $('#formSearchTable').hide();
    $("#download").prop('disabled', true);
    $('#collapseSearch').collapse(false)
  }

  $('#formSearchButton').on('click', function () {
    runFormSearchQuery();
  });
  $('#switchViewButton').on('click', function () {
    let buttonVal = $('#switchViewButton').val()
    if (buttonVal == 'advanced') {
      $('#switchViewButton').val('simple')
      $('#switchViewButton').html('Switch To Advanced View')
    } else {
      $('#switchViewButton').val('advanced')
      $('#switchViewButton').html('Switch To Simple View')
    }
    runFormSearchQuery();
  });
  $('#addUserToDept').on('click', function () {
    $("#addSupervisorToDeptModal").modal("show");
    $('#addUser').prop('disabled', true)
  })
  $("#sortByButton").on('click', function () {
    var isDisabled = $('#fieldPicker').prop('disabled');
    if (!isDisabled && $('#fieldPicker').val() == '') {
      msgFlash("Cannot sort without selecting a field.", 'warning')
      return
    }
    runFormSearchQuery()
  })

  if ($('#formSearchTable').is(':hidden')) {
    $('#columnPicker').selectpicker('hide')
    $('#fieldPicker').selectpicker('hide')
    $('#orderPicker').selectpicker('hide')
    $('#sortByButton').hide()
  }

  $('#addUser').on('click', function () {
    let supervisorID = $('#supervisorModalSelect :selected').val()
    let departmentID = $('#departmentModalSelect :selected').val()

    addSupervisorToDepartment(supervisorID, departmentID)
  })
  $('#departmentModalSelect').on('change', disableButtonHandler)
  $('#supervisorModalSelect').on('change', disableButtonHandler)
  $('#firstName').on('click', function () {
    $("#lastName").removeAttr("checked");
    runFormSearchQuery()
  })
  $('#lastName').on('click', function () {
    $("#firstName").removeAttr("checked");
    runFormSearchQuery()
  })

  $('#clearSelectionsButton').on('click', function () {
    $("input:checkbox").removeAttr("checked");
    clearDropdowns()
  });

  $(function () {
    $("#formSearchAccordion").accordion({
      collapsible: true
    });
  });
  $(function () {
    $("#formSearchAccordion").accordion();
    $("#formSearchAccordion .ui-accordion-header").css({ fontSize: 20 });// width of the box content area
  });
  // listening for preset button clicks.
  $('#mySupervisees').on('click', function () {
    $("input:checkbox").removeAttr("checked");
    runFormSearchQuery("mySupervisees");
  });
  $('#superviseesPendingForms').on('click', function () {
    $("input:checkbox").removeAttr("checked");
    runFormSearchQuery("pendingForms");
  });
  $('#currentTerm').on('click', function () {
    runFormSearchQuery("currentTerm");
  });
  $('#columnPicker').on('change', function () {
    let column = $('#columnPicker :selected').text()
    let fields = columnFieldMap[column]

    // clear the options from the current field picker and replace 
    // them with the ones from the columnFieldMap 
    $('#fieldPicker').empty();
    fields.forEach((field) => {
      var option = $('<option>', {
        value: field[1],
        text: field[0]
      });
      $('#fieldPicker').append(option)
    })

    // if there is only one field then that means we can disable the fieldPicker and rely
    // on the column instead
    if (fields.length === 1) {
      $('#fieldPicker').prop('disabled', true);

    } else {
      $('#fieldPicker').prop('disabled', false);
    }
    $('.selectpicker').selectpicker('refresh')
  })
});

// this is a mapping which maps the column option to its field options.
// many do not have multiple fields so the field is just the column itself (e.g. term)
const columnFieldMap = {
  'Term': [['Term', 'term']],
  'Department': [['Department', 'department']],
  'Supervisor': [['First name', 'supervisorFirstName'], ['Last Name', 'supervisorLastName']],
  'Student': [['First name', 'studentFirstName'], ['Last Name', 'studentLastName']],
  'Position (WLS)': [['Position Type', 'positionType'], ['WLS', 'positionWLS'], ['Position Code', 'positionCode']],
  'Hrs.': [['Hours', 'hours']],
  'Length': [['Length', 'length']],
  'Created By': [['Created By', 'createdBy']],
  'Form Type (Status)': [['Form Type', 'formType'], ['Status', 'formStatus']]
};


function disableButtonHandler() {
  if ($('#departmentModalSelect :selected').val() == "" || $('#supervisorModalSelect :selected').val() == "") {
    $('#addUser').prop('disabled', true)
  }
  else {
    $('#addUser').prop('disabled', false)
  }
}

function runFormSearchQuery(button) {
  let view = $('#switchViewButton').val()
  let termCode, departmentID, supervisorID, studentID;
  let formStatusList = [];
  let formTypeList = [];
  var isDisabled = $('#fieldPicker').prop('disabled');
  let sortBy = $('#fieldPicker').val()

  // if the fieldPicker is disabled that means we should take the value
  // from the columnPicker instead
  if (isDisabled) {
    sortBy = $('#columnPicker').val()
  }
  let order = $('#orderPicker').val()

  switch (button) {
    case "mySupervisees":
      termCode = "currentTerm"
      departmentID = ""
      supervisorID = "currentUser"
      studentID = ""
      formStatusList = []
      break;

    case "pendingForms":
      termCode = "currentTerm"
      departmentID = ""
      supervisorID = "currentUser"
      studentID = ""
      formStatusList = ["Pending", "Pre-Student Approval"]
      break;

    case "currentTerm":
      termCode = "currentTerm"
      departmentID = ""
      supervisorID = ""
      studentID = ""
      formStatusList = []
      formTypeList = []
      break;

    default:
      termCode = $("#termSelect").val();
      departmentID = $("#departmentSelect").val();
      supervisorID = $("#supervisorSelect").val();
      studentID = $("#studentSelect").val();
      formStatusList = $("input:checkbox[name='formStatus']:checked").map((i, el) => el.value).get();
      formTypeList = $("input:checkbox[name='formType']:checked").map((i, el) => el.value).get();
  }

  queryDict = {
    // this may seem counterintuitive but since the value
    // switches on button press it is technically the opposite of the current view
    'view': view,
    'termCode': termCode,
    'departmentID': departmentID,
    'supervisorID': supervisorID,
    'studentID': studentID,
    'formStatus': formStatusList,
    'formType': formTypeList,
    'sortBy': sortBy,
    'order': order
  };
  setFormSearchValues(queryDict)
  data = JSON.stringify(queryDict)

  var inAnHour = new Date(new Date().getTime() + 60 * 60 * 1000);
  Cookies.set('lsfSearchResults', data, { expires: inAnHour })
  if (view == 'advanced') {
    createDataTable(data)
  } {
    // fetchSimpleView(data)
  }
}

function fetchSimpleView(data) {
  data = JSON.stringify(queryDict)
  return $.ajax({
    method: "POST",
    url: `/`,
    data: data,
    success: function (response) {
      renderSimpleView(response)
    },
    error: function () {
    },
  })
}

function renderSimpleView(html) {
  $('#formSearchTable').hide();
  $('#simpleView').html(html)
}

function createDataTable(data) {
  $("#formSearchAccordion").accordion({ collapsible: true, active: false });
  $("#download").prop('disabled', false);
  $('#formSearchTable').show();
  $('#simpleView').hide()
  $('#columnPicker').selectpicker('show')
  $('#fieldPicker').selectpicker('show')
  $('#orderPicker').selectpicker('show')
  $('#sortByButton').show()

  // default ordering upon initialization is term
  $('#formSearchTable').DataTable({
    responsive: true,
    destroy: true,
    searching: false, // we may want to enable this at some point, think it may require custom logic on our end, though.
    processing: true,
    serverSide: true,
    paging: true,
    lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    pageLength: 25,
    columnDefs: [{
      // this disables built in ordering on columns with these IDs 
      // (may be a way to do without specifying each individually but idk)
      targets: [0, 1, 2, 3, 4, 5, 6, 7, 8],
      orderable: false,
    }],
    ajax: {
      // we fetch the data and do the ordering server side which means all logic is done
      // in Python and the datatable just displays the results
      url: "/",
      type: "POST",
      data: { 'data': data },
      dataSrc: "data",
    }
  });
}

function setFormSearchValues(searchDict) {

  if (searchDict.termCode == "currentTerm") {
    $("#termSelect").selectpicker("val", g_currentTerm);
  } else {
    $("#termSelect").selectpicker("val", searchDict.termCode);
  }
  if (searchDict.supervisorID == "currentUser") {
    $("#supervisorSelect").selectpicker("val", g_currentUser);
  } else {
    $("#supervisorSelect").selectpicker("val", searchDict.supervisorID);
  }
  $("#departmentSelect").selectpicker("val", searchDict.departmentID);
  $("#studentSelect").selectpicker("val", searchDict.studentID);

  $(searchDict.formType).each(function (i, value) {
    $(`input:checkbox[value='${value}']`).prop('checked', true);
  })
  $(searchDict.formStatus).each(function (i, value) {
    $(`input:checkbox[value='${value}']`).prop('checked', true);
  })
}

