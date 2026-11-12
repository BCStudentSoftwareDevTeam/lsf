$(function () {
    const form = $("#positionImportForm");
    const result = $("#importResult");
    const buttons = $("#importSelectedButton, #importAllButton");

    let importing = false;

    function showError(message) {
        result
            .empty()
            .removeClass("alert-info alert-success alert-warning")
            .addClass("alert alert-danger")
            .text(message);
    }

    function runImport(importAll) {
        if (importing) {
            return;
        }

        const requiredInputs = [
            "#boxClientID",
            "#boxClientSecret",
            "#boxAccessToken",
            "#boxFolderID"
        ];

        for (const selector of requiredInputs) {
            if (!$(selector)[0].reportValidity()) {
                return;
            }
        }

        const revisionStart = $("#importRevisionStart").val();
        const revisionEnd = $("#importRevisionEnd").val();

        if (!importAll) {
            if (
                !$("#importRevisionStart")[0].reportValidity()
                || !$("#importRevisionEnd")[0].reportValidity()
            ) {
                return;
            }

            if (
                revisionStart
                && revisionEnd
                && revisionStart > revisionEnd
            ) {
                showError(
                    "The start date must be on or before the end date."
                );
                return;
            }
        }

        const payload = {
            boxClientID: $("#boxClientID").val().trim(),
            boxClientSecret: $("#boxClientSecret").val().trim(),
            boxAccessToken: $("#boxAccessToken").val().trim(),
            boxFolderID: $("#boxFolderID").val().trim(),

            departmentID: importAll
                ? ""
                : $("#importDepartment").val(),

            wls: importAll
                ? ""
                : $("#importWls").val(),

            revisionStart: importAll ? "" : revisionStart,
            revisionEnd: importAll ? "" : revisionEnd
        };

        const csrfToken = form
            .find('input[name="csrf_token"]')
            .val();

        importing = true;
        buttons.prop("disabled", true);
        form.attr("aria-busy", "true");

        result
            .empty()
            .removeClass("alert-success alert-danger alert-warning")
            .addClass("alert alert-info")
            .text("Importing documents from Box. Please wait…");

        $.ajax({
            url: form.attr("action"),
            type: "POST",
            contentType: "application/json",
            dataType: "json",
            data: JSON.stringify(payload),
            headers: csrfToken
                ? { "X-CSRFToken": csrfToken }
                : {}
        })
        .done(function (response) {
            result
                .empty()
                .removeClass("alert-info alert-success alert-danger alert-warning")
                .addClass(
                    response.failed > 0
                        ? "alert-warning"
                        : "alert-success"
                );

            $("<p>")
                .text(
                    `Imported: ${response.imported}. ` +
                    `Already existing: ${response.existing}. ` +
                    `Outside filters: ${response.filtered}. ` +
                    `Failed: ${response.failed}.`
                )
                .appendTo(result);

            if (response.errors && response.errors.length > 0) {
                const errorList = $("<ul>");

                response.errors.forEach(function (error) {
                    $("<li>")
                        .text(`${error.file}: ${error.message}`)
                        .appendTo(errorList);
                });

                result.append(errorList);
            }
        })
        .fail(function (xhr) {
            const message = (
                xhr.responseJSON
                && xhr.responseJSON.error
            ) || (
                "The connection was interrupted or the import failed. " +
                "Some documents may already have been imported. " +
                "Existing revisions will be skipped when you retry."
            );

            showError(message);
        })
        .always(function () {
            importing = false;
            buttons.prop("disabled", false);
            form.removeAttr("aria-busy");
        });
    }

    form.on("submit", function (event) {
        event.preventDefault();
        runImport(false);
    });

    $("#importAllButton").on("click", function () {
        runImport(true);
    });
});