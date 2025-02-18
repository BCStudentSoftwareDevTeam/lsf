document.addEventListener("DOMContentLoaded", function() {
    let checkbox = document.getElementById("laborConfirmationCheckbox");
    let acceptButton = document.getElementById("acceptButton");

    checkbox.addEventListener("change", function() {
        acceptButton.disabled = !checkbox.checked;
    });
});