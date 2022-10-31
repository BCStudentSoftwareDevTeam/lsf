$(document).ready(function(){
  $('#formSearchTable').hide();
  $("#download").prop('disabled', true);
  $('#collapseSearch').collapse(false)

  $('#formSearchButton').on('click', function(){
    runformSearchQuery();
  });

  $('#clearSelectionsButton').on('click', function(){
    $("input:radio:checked").removeAttr("checked");
    $('select.selectpicker').each(function() {
      $(`#${this.id} option:eq(0)`).prop("selected", true);
      $(`#${this.id}`).selectpicker("refresh");
    });
  });
});



function runformSearchQuery() {

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

  if (evaluationList.length > 0 && termCode == "") {
    $("#flash_container").html('<div class="alert alert-danger" role="alert" id="flasher">Term must be selected with evaluation status.</div>');
    $("#flasher").delay(5000).fadeOut();
  }
  else {
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
              error: function(request, status, error) {
                      location.reload();
                    }
        }
    });
  }
}
