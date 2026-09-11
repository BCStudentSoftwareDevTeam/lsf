$(document).ready(function() {

    $('#manageMembers').DataTable({
        'columnDefs': [{
            'targets': '.no-sorting',
            'orderable': false
        }], // hide sort icon on header of first column
        'aaSorting': [
        [0, 'asc']
         ], // start to sort data in second column
        searching: false, 
        pageLength: 10,
        language: {
        lengthMenu: " _MENU_ entries per page"
        },
        //dom: '<"top"l>rt<"bottom"p><"clear">' 
    });
    $('[data-toggle="popover"]').popover();
    setTimeout(function() { $(".alert-danger").fadeOut();}, 5000);
    $(document).on("click", ".assign-coordinator", function() {

        let memberName = $(this).data("member-name");
        let supervisorID = $(this).data("supervisor");
        let departmentID = $(this).data("department");
        let isChecked = $(this).is(":checked");
        
        $.ajax({
            url: "/members/update_coordinator",
            data: { supervisorID: supervisorID, departmentID: departmentID, isCoordinator: isChecked },
            type: "POST",
            success: function() {
                if (isChecked) {
                    $("#flash_container").html("<div class=\"alert alert-success\" role=\"alert\" id=\"flasher\">" + memberName + " has been assigned as a coordinator.</div>");
                    $("#flasher").delay(3000).fadeOut();
                } else {
                    $("#flash_container").html("<div class=\"alert alert-danger\" role=\"alert\" id=\"flasher\">" + memberName + " is no longer a coordinator.</div>");
                    $("#flasher").delay(3000).fadeOut();
                }
        
            },
            error: function() {console.log("An error has occured.");}
        })	

        
    });

    $(document).on("change", ".member-status-toggle", function() {
        let toggle = $(this);
        let banBadge = toggle.closest("tr").find(".isbanned-badge");

        let memberName = toggle.data("member-name");
        let supervisorID = toggle.data("supervisor");
        let isIneligible = toggle.is(":checked");

        $.ajax({
            url: "/members/update_eligibility",
            data: { supervisorID: supervisorID },
            type: "POST",
            success: function() {
                if (isIneligible) {
                    banBadge.css("visibility", "visible");
                    $("#flash_container").html("<div class=\"alert alert-danger\" role=\"alert\" id=\"flasher\">" + memberName + " is no longer eligible.</div>");
                } else {
                    banBadge.css("visibility", "hidden");
                    $("#flash_container").html("<div class=\"alert alert-info\" role=\"alert\" id=\"flasher\">" + memberName + " is eligible now.</div>");
                }

                $("#flasher").delay(3000).fadeOut();
            },
            error: function() {
                toggle.prop("checked", !isIneligible);
                console.log("An error has occurred.");
            }
        });
    });

    $(document).on("click", ".remove-member", function() {

        let redButton = $(this);
        let row = $(this).closest("tr");

        let memberName = redButton.data("member-name");
        let supervisorID = redButton.data("supervisor");
        let departmentID = redButton.data("department");

    
        $.ajax({
            url: "/members/remove",
            data: { supervisorID: supervisorID, departmentID: departmentID },
            type: "DELETE",
            success: function() {
                $("#flash_container").html("<div class=\"alert alert-danger\"alert\" id=\"flasher\">" + memberName + " has been removed from the department.</div>");
                $("#flasher").delay(3000).fadeOut();
                row.remove();
            },
            
        })	
    });
})

// Creates a dom fragment from html, rather than having to add dom elements
// https://love2dev.com/blog/inserting-html-using-createdocumentfragment-instead-of-using-jquery/
function createFragment(htmlStr) {
    let frag = document.createDocumentFragment(), temp = document.createElement('div');
    temp.innerHTML = htmlStr;
    while(temp.firstChild) { frag.appendChild(temp.firstChild); }
    return frag;
}

// highlight search string. doesn't actually check for last name and first name, just highlights what we find
$.fn.selectpicker.Constructor.DEFAULTS.whiteList.mark = [];
function highlight(htmlStr, query) {
    query = query.trim().split(" ");
    for( let i = 0; i < query.length; i++) {
        htmlStr = htmlStr.replace(new RegExp(query[i], "gi"), function(match) { return `<mark>${match}</mark>`; });
    }
    return htmlStr;
}

let typeTimer;

$('#search').selectpicker('refresh');
$('.dropdown-menu .bs-searchbox input').on('keyup', function (e) {
    // ignore arrow keys
    if (e.keyCode == '40' || e.keyCode == '38') return;

    // wait a little longer for bnumber typing
    let keyInterval = 200
    if (e.keyCode >= 48 && e.keyCode <= 57) {
        keyInterval = 500
    }

    // don't search for every key (especially relevant for bnumber)
    clearTimeout(typeTimer)
    typeTimer = setTimeout(function() { sendQuery(e.target.value); }, keyInterval)
});

$('#search').on('changed.bs.select', function () {
    let supervisorID = $(this).val();
    let departmentID = $(this).data('department-id');

    if (!supervisorID || !departmentID) return;

    addSupervisorToDepartment(supervisorID, departmentID, function() {
      window.location.reload();
    });
});

// We load the options returned into an html string and then add them to the selectpicker at the end, to save A LOT of time.
function sendQuery(search_str) {
    $("#search").empty();
    $('#search').selectpicker("refresh");
    if (search_str.length >= 3) {
      $.ajax({
        type: "GET",
        url: "/members/search/" + encodeURIComponent(search_str),
        contentType: 'application/json',
        success: function(response) {
          let optionString = ""
          for (let key = 0; key < response.length; key++) {
            let username = response[key]['username'];
            let bnumber = response[key]['bnumber'];
            let firstName = response[key]['firstName'];
            let lastName = response[key]['lastName'];
            let type = response[key]['type'];
            if (type == "Supervisor") {
              let choice_text = bnumber + ': ' + firstName + ' ' + lastName;
              let highlighted_text = highlight(choice_text, search_str) + `<small class='text-muted'>${username}</small>`;
              optionString += `<option value="${bnumber}" data-content="${highlighted_text}" data-subtext="${username}">${choice_text}</option>`;
            }
        }
          $("#search").append(createFragment(optionString))
          $('#search').selectpicker("refresh");
        }
      });
    }
}