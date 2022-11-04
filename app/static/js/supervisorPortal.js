$(document).ready(function(){
  if (String(window.location.pathname) === "/") {
        console.log(parseCookie(document.cookie))
        runformSearchQuery(parseCookie(document.cookie), true);
  } else {
      $('#formSearchTable').hide();
      $("#download").prop('disabled', true);
      $('#collapseSearch').collapse(false)
  }
  $('#formSearchButton').on('click', function(){
    runformSearchQuery(newData='', false);
  });

  $('#clearSelectionsButton').on('click', function(){
    $("input:radio:checked").removeAttr("checked");
    $('select.selectpicker').each(function() {
      $(`#${this.id} option:eq(0)`).prop("selected", true);
      $(`#${this.id}`).selectpicker("refresh");
    });
  });
});

const parseCookie = str =>
  str
  .split(';')
  .map(v => v.split('='))
  .reduce((acc, v) => {
    return decodeURIComponent(v[1].trim());
  }, {});

function runformSearchQuery(newData='', cookie) {

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
  queryDict = {'termCode': termCode,
               'departmentID': departmentID,
               'supervisorID': supervisorID,
               'studentID': studentID,
               'formStatus': formStatusList,
               'formType': formTypeList,
               'evaluations': evaluationList
             };
  data = JSON.stringify(queryDict)
  if (cookie) {
      data = newData
  }
  let now = new Date();
  now.setMinutes(now.getMinutes() + 1);
  document.cookie = "searchResults="+data +"; expires" + now.toUTCString() +";"
  if(true) {
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
              dataSrc: "data"
        }
    });
  }
}
