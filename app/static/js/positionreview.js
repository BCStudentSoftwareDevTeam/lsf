$(document).ready(function () {
    $('#positionreviewtable').DataTable({
        pageLength: 25,
	    columnDefs: [{ width: '20%', targets: 0 },{ width: '20%', targets: 1 }]
    });
});