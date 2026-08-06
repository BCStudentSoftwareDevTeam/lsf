$(document).ready( function(){
    function initTable(selector) {
        return $(selector).DataTable({
            pageLength: 25,
            info: false,
            lengthChange: false,
            searching: false,
            paging: false,
            order: []
        });
    }
    
    const fallTermPrimaries = initTable('#fallTermPrimaries');
    const fallTermSecondaries = initTable('#fallTermSecondaries');
    const springTermPrimaries = initTable('#springTermPrimaries');
    const springTermSecondaries = initTable('#springTermSecondaries');
    const breakTable = initTable('#breakTable');
});