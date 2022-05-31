let table;

$(document).ready(function() {
  createButtons();
  if (document.location.href.endsWith('/')) {
    // index page, loads current supervisees
    $("#userDepartments").hide();
  } else {
    // departmental page, loads all departmental students
    $("#placeholder").hide()
    // If the select picker already has a department selected when the page is loaded,
    // then we want to populate the data table with the selected department
    let departmentDropDown = $("#departmentDropDown");
    let departmentSelected = $('option:selected', departmentDropDown).attr('value');
    if (departmentSelected) {
      populateTable();
    }
  }
  table.columns(1)
       .search("Pending")
       .draw();

  $('#studentList').show();
  $('#download').show();

  $("#download").click(function() {
    selectAll = $("#selectAllLabel");
    $("#downloadModalText").empty();
    $("#downloadModalText").append(selectAll);

    var bnums = [];
    $.each(table.rows({selected: true, filter: "applied"}).data(), function () {
      hiddenName=$($.parseHTML($(this)[1])[2]).text()
      hiddenBnum=$($.parseHTML($(this)[1])[4]).text()
      if ($.inArray(hiddenBnum, bnums) == -1){
          $("#downloadModalText").append(`<div class="checkbox"><label class="container"><input class="checkbox" type="checkbox" name="${hiddenBnum}" id="${hiddenBnum}" value="${hiddenBnum}"/>${hiddenName}</label></div>`)
          bnums.push(hiddenBnum);
      }
    })

    //FIXME: This is intended to close the Download modal after they get the file. It doesn't work because we use flask-bootstrap. Leaving here for the next person.
    // $("#submitButton").on("click", function() {
    //   $('#downloadModal').modal('hide');
    // })
  });

  // Listen for click on toggle checkbox
  $('#downloadModalText').on('change', '#selectAll', function () {
      if(this.checked) {
          // Iterate each checkbox
          $(':checkbox').not("[disabled]").each(function() {
              this.checked = true;
          });
      } else {
          $(':checkbox').not("[disabled]").each(function() {
              this.checked = false;
          });
      }
  });
});

function createButtons() {
  table = $("#studentList").DataTable({
    "drawCallback": function( settings ) {
      $("#studentList thead").remove(); } , // Used to hide the data table header
    "columnDefs":[
      {"visable": false, "target": [1]}
    ],
     "order": [[0, "desc"]], //display order on column
     "pagingType": "simple_numbers",
     "ordering": false,
     "info": false,
     "lengthChange": false,
     dom: 'Bfrtip',
     initComplete: function() {
       // Function used to remove the default class given to datatable buttons, and
       // give buttons bootstrap classes instead
       let btns = $('.dt-button');
       btns.addClass('btn btn-light');
       btns.removeClass('dt-button');
       $("#Pending_id").removeClass("btn-light").addClass("btn-primary");
     },
     // Used to created the buttons rendered by the data table
     buttons: addButtons()
   }
 )
};

function addButton(value, index) {
  tabs.push({
      text: value,
      attr: {id: value + "_id",
             class: "btn allButtons"},
      action: function ( e, dt, node, config ) {
        table.column(1)
             .search(value)
             .draw();
        $(".allButtons").removeClass("btn-primary");
        $(node).addClass("btn btn-primary").removeClass("btn-light");
      }
  });
};

function addButtons() {
 tabs = [];
 tableTabs.forEach(addButton);
 return tabs
}


function downloadHistory() {
  $('input[type="checkbox"]:checked').prop('checked',false);
}

// variable to check if another ajax call is in progress
let currentRequest = null;
function populateTable(){
  // if a second department is selected while the first department is loading
  // the previous ajax call will be aborted and the last ajax call will continue
  if (currentRequest != null) {
    currentRequest.abort();
  }
  // This function will take input from the department select picker, and based
  // off of what department is choosen, the function will populate both the data table
  // and the modal with the correct data from that department

  // This grabs the department selected from the select picker
  let departmentDropDown = $("#departmentDropDown");
  let departmentSelected = $('option:selected', departmentDropDown).attr('value');

  // AJAX call sends our controller the department choosen, and the controller
  // should send back the data we need as JSON
  currentRequest = $.ajax({
    method: "GET",
    url: "/main/department/selection/" + departmentSelected,
    datatype: "json",
    success: function(response) {
      table.rows().clear();
      // Parse the JSON we get back from the controller
      response = JSON.parse(response)

      // This section will iterate through the JSON data, and access the values
      // from the key-value pairs that we will need to populate both the modal and the
      // data table
      currentForms = true
      for (key in response) {
        if (response[key] == "") {
          currentForms = false
          continue;
        }
        if (currentForms == true) {
          formStatus = response[key].status.statusName
        } else {
          formStatus = "Past Student"
        }

        let bNumber = response[key].formID.studentSupervisee.ID
        let student = response[key].formID.studentName
        let term = response[key].formID.termCode.termName
        let position = response[key].formID.POSN_TITLE
        let positionType = response[key].formID.jobType[0]
        let department = response[key].formID.department.DEPT_NAME

        table.row.add([`<div class="row">
                          <a href='/laborHistory/${departmentSelected}/${bNumber}' value=0>
                            <span class='h4'>${student} (${bNumber}) </span>
                            <span class="h6"> (${positionType}) ${position}</span>
                          </a>
                          <span class='pushRight h5'>${formStatus}</span>
                        </div>
                        <div class="row">
                        <span class='pushLeft h6'>${term}</span>
                        <span class='pushRight h6'>${department}</span>`,
                        `<span style='display:none'>${formStatus}, ${term}</span>
                        <span style='display:none' id="hiddenStudentName">${student}</span>
                        <span style='display:none' id="hiddenBnumber">${bNumber}</span>`])
      }
      table.draw();
    }
  })
}
