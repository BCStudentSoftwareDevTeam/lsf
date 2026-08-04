$(document).ready( function(){
    fallTermPrimaries = $('#fallTermPrimaries');
    fallTermPrimaries.DataTable({
        pageLength: 25,
        info: false,
        lengthChange: false,
        searching: false,
        paging: false,
        "order": []
    });
    fallTermSecondaries = $('#fallTermSecondaries');
    fallTermSecondaries.DataTable({
        pageLength: 25,
        info: false,
        lengthChange: false,
        searching: false,
        paging: false,
        "order": []
    });

    springTermPrimaries = $('#springTermPrimaries');
    springTermPrimaries.DataTable({
        pageLength: 25,
        info: false,
        lengthChange: false,
        searching: false,
        paging: false,
        "order": []
    });
    springTermSecondaries = $('#springTermSecondaries');
    springTermSecondaries.DataTable({
        pageLength: 25,
        info: false,
        lengthChange: false,
        searching: false,
        paging: false,
        "order": []
    });
    breakTable = $('#breakTable');
    breakTable.DataTable({
        pageLength: 25,
        info: false,
        lengthChange: false,
        searching: false,
        paging: false,
        "order": []
    });
});