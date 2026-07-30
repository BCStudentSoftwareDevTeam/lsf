$(document).ready( function(){
    const entriesPerYear = 5;

    allocationTable = $('#allocationTable');
    allocationTable.DataTable({
        paging: true,
        searching: true,
        pageLength: 5,
        lengthMenu:[[5,10,20,50,-1],
        ['5', '10', '20', '50', 'All']],
        "order": [
            0, "desc"
        ]
    });
});