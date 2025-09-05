$(document).ready(function () {
  $('#formSearchButton').on('click', function () {
    runFormSearchQuery();
    $('#sortOptions').show();
  });

  $('#switchViewButton').on('click', function () {
    // toggle the view and button value
    buttonVal = $("#switchViewButton").val()
    switchViewButton((buttonVal == "simple") ? "advanced" : "simple")

    // we can just rerun the form search query as it pulls down the value
    // of the button to determine what button to render
    runFormSearchQuery();
    $('#sortOptions').show();
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

  if ($('#columnPicker').val() == '') {
    $('#fieldPicker').prop('disabled', true)
    $('.selectpicker').selectpicker('refresh')
  }

  $('#addUser').on('click', function () {
    let supervisorID = $('#supervisorModalSelect :selected').val()
    let departmentID = $('#departmentModalSelect :selected').val()

    addSupervisorToDepartment(supervisorID, departmentID)
  })

  $('#departmentModalSelect').on('change', disableButtonHandler)
  $('#supervisorModalSelect').on('change', disableButtonHandler)

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
    buttonVal = $("#switchViewButton").val()
    let fields = buttonVal == "advanced" ? advancedColumnFieldMap[column] : simpleColumnFieldMap[column];

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

  ////////////////////////////////////////////
  // check the cookie and GO!
  if ((document.cookie).includes("lsfSearchResults=")) {
    cookieStr = Cookies.get('lsfSearchResults')
    cookieJSON = JSON.parse(cookieStr)

    // using the cookies, make sure the view is properly set as well
    if (cookieJSON.view == 'advanced') {
      createDataTable(cookieStr)
      switchViewButton('advanced')
    } else {
      fetchSimpleView(cookieStr)
      switchViewButton('simple')
    }
    setFormSearchValues(cookieJSON)

  } else {
    $('#formSearchTable').hide();
    $('#sortOptions').hide();
    $("#download").prop('disabled', true);
    $('#collapseSearch').collapse(false)

    // select current supervisees if nothing selected
    $('#mySupervisees').trigger("click")
  }

  // Live search handling for dropdowns
  $("#termSelectParent .bs-searchbox input").on("keyup", function(e) {
    liveSearch("termSelect", e);
  });
  $("#departmentSelectParent .bs-searchbox input").on("keyup", function(e) {
    liveSearch("departmentSelect", e);
  });
  $("#supervisorSelectParent .bs-searchbox input").on("keyup", function(e) {
    liveSearch("supervisorSelect", e);
  });
  $("#studentSelectParent .bs-searchbox input").on("keyup", function(e) {
    liveSearch("studentSelect", e);
  });

});

// this is a mapping which maps the column option to its field options.
// many do not have multiple fields so the field is just the column itself (e.g. term)
const advancedColumnFieldMap = {
'Term': [['Term', 'term']],
'Department': [['Department', 'department']],
'Supervisor': [['First name', 'supervisorFirstName'], ['Last Name', 'supervisorLastName']],
'Student': [['First name', 'studentFirstName'], ['Last Name', 'studentLastName']],
'Position (WLS)': [['WLS', 'positionWLS'], ['Position Type', 'positionType'], ['Position Title', 'positionTitle']],
'Length': [['Length', 'length']],
'Created By': [['Created By', 'createdBy']],
'Form Type (Status)': [['Form Type', 'formType'], ['Status', 'formStatus']]
};

const simpleColumnFieldMap = {
'Term': [['Term', 'term']],
'Department': [['Department', 'department']],
'Student': [['First name', 'studentFirstName'], ['Last Name', 'studentLastName']],
'Position': [['Position Type', 'positionType'], ['Position Title', 'positionTitle']],
'Form Status': [['Status', 'formStatus']]
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
let currentView = $('#switchViewButton').val()
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
      formStatusList = ["Approved"]
      if (currentView == "simple") { // avoid duplicates in the table
        formTypeList = ["Labor Status Form"]
      }
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
      if (currentView == "simple") { // avoid duplicates in the table
        formTypeList = ["Labor Status Form"]
      }
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
    'view': currentView,
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
  if (currentView === 'advanced') {
    createDataTable(data)
  } else {
    fetchSimpleView(data)
  }
}

function resetColumns(columnFieldMap) {
  // clear the current columnPicker options and populate it with new ones
  // from either the simple or advanced columnFieldMap
  $('#columnPicker').empty();
  let columns = Object.keys(columnFieldMap)
  columns.forEach((column) => {
    var option = $('<option>', {
      value: columnFieldMap[column][0][1],
      text: column
    });
    $('#columnPicker').append(option)
  })
}

function switchViewButton(targetView) {
  if (targetView == 'simple') {
    $('#switchViewButton').val('simple')
    $('#switchViewButton').html('Switch To Advanced View')
    resetColumns(simpleColumnFieldMap) 

  } else {
    $('#switchViewButton').val('advanced')
    $('#switchViewButton').html('Switch To Simple View')
    resetColumns(advancedColumnFieldMap) 
  }
  $('.selectpicker').selectpicker('refresh')
}

function fetchSimpleView(data) {
  $('#formSearchTable').hide();
  $('#formSearchTable_wrapper').hide();
  $('#simpleView').show();
  $('#columnPicker').selectpicker('show')
  $('#fieldPicker').selectpicker('show')
  $('#orderPicker').selectpicker('show')
  $('#sortByButton').show()

  $('#simpleView').DataTable({
    responsive: true,
    destroy: true,
    searching: false, // we may want to enable this at some point, think it may require custom logic on our end, though.
    processing: true,
    serverSide: true,
    paging: true,
    lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    pageLength: 50,
    columnDefs: [{
      // this disables built in ordering on columns with these IDs 
      // (may be a way to do without specifying each individually but idk)
      targets: [0],
      orderable: false,
    }],
    ajax: {
      // we fetch the data and do the ordering server side which means all logic is done
      // in Python and the datatable just displays the results
      url: "/",
      type: "POST",
      data: { 'data': data },
      dataSrc: function(response) {
        $('#downloadId').val(response.downloadId);
        updateDownloadButton(response)
        return response.data;
      }
    }
  });
}

function createDataTable(data) {
  $("#formSearchAccordion").accordion({ collapsible: true, active: false });
  $("#download").prop('disabled', true);
  $('#formSearchTable').show();
  $('#simpleView').hide()
  $('#simpleView_wrapper').hide();
  $('#columnPicker').selectpicker('show')
  $('#fieldPicker').selectpicker('show')
  $('#orderPicker').selectpicker('show')
  $('#sortByButton').show()

  // default ordering upon initialization is term
  let table = $('#formSearchTable').DataTable({
    responsive: true,
    destroy: true,
    searching: false, // we may want to enable this at some point, think it may require custom logic on our end, though.
    processing: true,
    serverSide: true,
    paging: true,
    lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    pageLength: 50,
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
    }
  });
  // catch the ajax data returning. Can't use the 'success' callback
  table.on('xhr.dt', function(e, settings, json, xhr) {
    updateDownloadButton(json)
  });

}

function updateDownloadButton(response){
 if (response.recordsTotal && response.recordsTotal > 0) {
          $("#download").prop('disabled', false);
        } else {
          $("#download").prop('disabled', true);
        }
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

const selectConfig = {
  termSelect: {
    defaults: [
      { value: "", text: "All terms" },
      { value: "activeTerms", text: "All Active Terms" }
    ],
    build: row => ({
      value: row.termCode,
      text: row.termName
    })
  },
  departmentSelect: {
    defaults: [{ value: "", text: "All departments" }],
    build: row => ({
      value: row.departmentID,
      text: row.DEPT_NAME,
      "data-content": row.isActive
        ? row.DEPT_NAME
        : `<div class='text-muted'>${row.DEPT_NAME} <small>--INACTIVE--</small></div>`
    })
  },
  supervisorSelect: {
    defaults: [{ value: "", text: "All supervisors" }],
    build: row => ({
      value: row.ID,
      text: `${row.FIRST_NAME} ${row.LAST_NAME} (${row.ID})`,
      "data-content": row.isActive
        ? `${row.FIRST_NAME} ${row.LAST_NAME} <small class='text-muted'> (${row.ID})</small>`
        : `<div class='text-muted'>${row.FIRST_NAME} ${row.LAST_NAME} <small>(${row.ID}) --INACTIVE--</small></div>`
    })
  },
  studentSelect: {
    defaults: [{ value: "", text: "All students" }],
    build: row => ({
      value: row.ID,
      text: `${row.FIRST_NAME} ${row.LAST_NAME} (${row.ID})`,
      "data-content": `${row.FIRST_NAME} ${row.LAST_NAME} <small class='text-muted'> (${row.ID})</small>`
    })
  }
};


function resetSelect(selectPickerID) {
  const $select = $("#" + selectPickerID);
  $select.empty();

  selectConfig[selectPickerID].defaults.forEach(option => {
    $select.append($("<option>", { value: option.value, text: option.text }));
  });

  $select.selectpicker("refresh");
}

function liveSearch(selectPickerID, e) {
    const searchQuery = e.target.value;
    if (searchQuery.length < 3) {
      resetSelect(selectPickerID);
      return;
    }

    const selectObject = $("#" + selectPickerID);
    const searchType = selectPickerID;

    $.ajax({
      type: "GET",
      url: "/supervisorPortal/liveSearch",
      data: {
              searchType: searchType,
              userInput: searchQuery
            },
      contentType: 'application/json',
      success: function(response) {
        selectObject.empty();
        const buildOption = selectConfig[selectPickerID].build;
        response.forEach(row => {
          const option = buildOption(row);
          console.log(option);
          selectObject.append($("<option>", option));
        });
        selectObject.selectpicker("refresh");
      }
    });
};

