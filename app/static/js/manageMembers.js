$(document).ready(function() {
    $('#manageMembers').DataTable({
        'columnDefs': [{
            'targets': [1, 2],
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
})

