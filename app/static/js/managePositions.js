$(document).ready(function () {
    $('#positionTable').DataTable({
        pageLength: 25,
        columnDefs: [
            { className: 'dt-head-center', targets: '_all' },
            { orderable: false, targets: [3] }
        ]
    });
});