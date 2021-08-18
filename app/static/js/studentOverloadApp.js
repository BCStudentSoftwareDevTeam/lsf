// checking the classification of student on page load
$(document).ready(function () {
  $("#notes").prop("disabled", true);
  $("#submit").prop("disabled", true);
  if ($("#Classification").val() == "Freshman"){
    $('#freshmanWarning').modal({
     backdrop: 'static',
     keyboard: false
  })
 }

});

checkboxCounter = 0; //keeps track of how many checkboxes are checked
function checkBoxCheck(obj,totalFormHours){
  if(obj.checked == true){
      checkboxCounter = checkboxCounter + 1;
  }
  else if(obj.checked == false){
      checkboxCounter = checkboxCounter - 1;
  }
  if(checkboxCounter >= 7 & totalFormHours > 20){
    $("#notes").prop("disabled", false);
  }
  else if (checkboxCounter >=5 & totalFormHours <= 20){
      $("#notes").prop("disabled", false);
  }
  else{
    $("#notes").prop("disabled", true);
  }
}

$(document).on('keyup', '#notes', function() {
  // this function makes sure that the text area has at least 1 character
  if ($.trim($(this).val()).length == 0) {
    $('#submit').prop("disabled", true);
  } else {
    $('#submit').prop("disabled", false);
  }
})

function checkForEmptyFields(){
  if($("#notes").val() != "") {
    $('#submitModal').modal('show');
  }
}

function updateDatabase(formID){
  var notes = $("#notes").val()
  var dataDict = {}
  dataDict[formID] = {"Notes": notes, "formID": formID}
  data = JSON.stringify(dataDict)
  var url = "/studentOverloadApp/update";
   $.ajax({
     url: url,
     method: "POST",
     data: data,
     dataType: "json",
     contentType: 'application/json'
   })
}
