$(document).ready(function () {
    var sectionsContainer = document.getElementById('sectionsContainer');
    var sectionRowTemplate = document.getElementById('sectionRowTemplate');

    document.getElementById('addSectionBtn').addEventListener('click', function () {
        sectionsContainer.appendChild(sectionRowTemplate.content.cloneNode(true));
    });

    sectionsContainer.addEventListener('click', function (event) {
        if (event.target.classList.contains('remove-section-btn')) {
            event.target.closest('.description-section-row').remove();
        }
    });
});
