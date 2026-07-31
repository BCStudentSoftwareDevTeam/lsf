$(document).ready( function(){
    fallTermTable = $('#fallTermTable');
    fallTermTable.DataTable({
        pageLength: 25,
        info: false,
        lengthChange: false,
        searching: false,
        paging: false
    });

    springTermTable = $('#springTermTable');
    springTermTable.DataTable({
        pageLength: 25,
        info: false,
        lengthChange: false,
        searching: false,
        paging: false
    });
    breakTable = $('#breakTable');
    breakTable.DataTable({
        pageLength: 25,
        info: false,
        lengthChange: false,
        searching: false,
        paging: false
    });
});