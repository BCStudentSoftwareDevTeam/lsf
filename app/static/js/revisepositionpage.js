$(document).ready(function () {
    var sectionsContainer = document.getElementById('sectionsContainer');
    var sectionRowTemplate = document.getElementById('sectionRowTemplate');

    function initEditor(row) {
        var textarea = row.querySelector('textarea[name="sectionContent[]"]');
        if (textarea) {
            CKEDITOR.replace(textarea);
        }
    }

    sectionsContainer.querySelectorAll('.description-section-row').forEach(initEditor);

    document.getElementById('addSectionBtn').addEventListener('click', function () {
        var fragment = sectionRowTemplate.content.cloneNode(true);
        var row = fragment.querySelector('.description-section-row');
        sectionsContainer.appendChild(fragment);
        initEditor(row);
    });

    sectionsContainer.addEventListener('click', function (event) {
        if (event.target.classList.contains('remove-section-btn')) {
            var row = event.target.closest('.description-section-row');
            var textarea = row.querySelector('textarea[name="sectionContent[]"]');
            var editor = textarea && CKEDITOR.instances[textarea.id];
            if (editor) {
                editor.destroy(true);
            }
            row.remove();
        }
    });
});
