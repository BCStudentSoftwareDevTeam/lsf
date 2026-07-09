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

    $(document).on("click", ".member-status-btn", function() {
        let  memberName = $(this).data("member-name");
        let memberStatus = $(this).data("member-status");
        let category;

        if (memberStatus === "Banned") {
            category = "danger";
        } else {
            category = "success";
        }
                
        let quote = String.fromCharCode(39);

        $("#flash_container").html("<div class=\"alert alert-" + category + "\" role=\"alert\" id=\"flasher\">The status for " + memberName + " has been set to " + quote + memberStatus + quote + ".</div>");
        $("#flasher").delay(3000).fadeOut();

        if (memberStatus === "Banned") {
            $(this).removeClass("btn-danger").addClass("btn-success");
            $(this).text("Unban");
            $(this).data("member-status", "Unbanned");
        } else {
            $(this).removeClass("btn-success").addClass("btn-danger");
            $(this).html("&nbsp; Ban &nbsp;");
            $(this).data("member-status", "Banned");
        }
    });

    $(document).on("click", ".remove-member", function() {
        let  memberName = $(this).data("member-name");
        $("#flash_container").html("<div class=\"alert alert-info\" role=\"alert\" id=\"flasher\">" + memberName + " has been removed from the department.</div>");
        $("#flasher").delay(3000).fadeOut();
    });

    $(document).on("click", ".assign-coordinator", function() {
        let  memberName = $(this).data("member-name");

        if ($(this).is(":checked")) {
            $("#flash_container").html("<div class=\"alert alert-success\" role=\"alert\" id=\"flasher\">" + memberName + " has been assigned as a coordinator.</div>");
            $("#flasher").delay(3000).fadeOut();
        } else {
            $("#flash_container").html("<div class=\"alert alert-info\" role=\"alert\" id=\"flasher\">" + memberName + " is no longer a coordinator.</div>");
            $("#flasher").delay(3000).fadeOut();
        }
        
    });
})

