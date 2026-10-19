$(document).ready(function() {
    $("#selectedDepartment").on("change",function() {
        deptData = $(this).find('option:selected').data();
        window.location = `/department/${deptData.org}/${deptData.account}`;
    });
});