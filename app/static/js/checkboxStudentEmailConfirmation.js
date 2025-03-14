document.addEventListener("DOMContentLoaded", function() {
    let firstCheckbox = document.getElementById("firstCheckbox");
    let secondCheckbox = document.getElementById("secondCheckbox");
    let thirdCheckbox = document.getElementById("thirdCheckbox");
    let fourthCheckbox = document.getElementById("fourthCheckbox");
    let acceptButton = document.getElementById("acceptButton");

    function checkCheckboxes() {
        notaccepted = !(firstCheckbox.checked && secondCheckbox.checked && thirdCheckbox.checked && fourthCheckbox.checked);
        $("input[name='confirmParticipation']").val(notaccepted ? 0 : 1)
        acceptButton.disabled = notaccepted
    }

    firstCheckbox.addEventListener("change", checkCheckboxes);
    secondCheckbox.addEventListener("change", checkCheckboxes);
    thirdCheckbox.addEventListener("change", checkCheckboxes);
    fourthCheckbox.addEventListener("change", checkCheckboxes);
});
