document.addEventListener("DOMContentLoaded", function () {
    const checkbox = document.getElementById("laborConfirmationCheckbox");
    const approveButton = document.getElementById("approveButton");

    checkbox.addEventListener("change", function () {
        approveButton.disabled = !checkbox.checked;
    });
});