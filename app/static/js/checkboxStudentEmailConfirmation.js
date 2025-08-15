function verifyAgreements() {
    let all = $("input[type=checkbox]").length
    let checked = $("input[type=checkbox]:checked").length
    let accepted = (all == checked)
    $("#confirmParticipation").val(accepted ? 1 : 0)
    $("#acceptButton")[0].disabled = !accepted
}

$(document).ready(function() {
    $("input[type=checkbox]").on("change", verifyAgreements)
});
