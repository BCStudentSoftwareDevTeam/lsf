$(document).ready( function(){
    fallTermTable = $('#fallTermTable');
    fallTermTable.DataTable({
        pageLength: 25,
        info: false,
        lengthChange: false,
        searching: false,
        paging: false
    });
});