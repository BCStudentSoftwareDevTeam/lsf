$(document).ready( function(){
    allocationTable = $('#allocationTable');
    allocationTable.DataTable({
        searching: true,
        pageLength: 25
    });
});