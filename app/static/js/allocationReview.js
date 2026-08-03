$(document).ready( function(){

    $('[data-toggle="popover"]').popover();
    
    // not allowing users to type anything in a numeric spinner
    $("input[type='number'].breakHoursNumericSpinner").keypress(function (evt) {
      evt.preventDefault();
    });
    $("input[type='number'].positionNumericSpinner").keypress(function (evt) {
      evt.preventDefault();
    });
});