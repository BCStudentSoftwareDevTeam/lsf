$(document).ready( function(){
    // not allowing users to type anything in a numeric spinner
    $("input[type='number'].breakHoursNumericSpinner").keypress(function (evt) {
      if (!/[0-9]/.test(evt.key)) {
        evt.preventDefault();
      }
    });
    $("input[type='number'].positionNumericSpinner").keypress(function (evt) {
      evt.preventDefault();
    });
});