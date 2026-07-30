$(document).ready( function(){
    // not allowing users to type anything in a numeric spinner
    $("input[type='number'].numericSpinner").keypress(function (evt) {
      evt.preventDefault();
    });
});