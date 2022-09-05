// Creates a dom fragment from html, rather than having to add dom elements
// https://love2dev.com/blog/inserting-html-using-createdocumentfragment-instead-of-using-jquery/
function createFragment(htmlStr) {
    let frag = document.createDocumentFragment(), temp = document.createElement('div');
    temp.innerHTML = htmlStr;
    while(temp.firstChild) { frag.appendChild(temp.firstChild); }
    return frag;
}

// highlight search string. doesn't actually check for last name and first name, just highlights what we find
$.fn.selectpicker.Constructor.DEFAULTS.whiteList.mark = [];
function highlight(htmlStr, query) {
    query = query.trim().split(" ");
    for(i = 0; i < query.length; i++) {
        htmlStr = htmlStr.replace(new RegExp(query[i], "gi"), function(match) { return `<mark>${match}</mark>`; });
    }
    return htmlStr;
}

let typeTimer;

$('#search').selectpicker('refresh');
$('#search').on('change', function(e) {
    window.location.href= "/laborHistory/" + $('#search').val();
});
$('.dropdown-menu .bs-searchbox input').on('keyup', function (e) {
    // ignore arrow keys
    if (e.keyCode == '40' || e.keyCode == '38') return;

    // wait a little longer for bnumber typing
    keyInterval = 200
    if (e.keyCode >= 48 && e.keyCode <= 57) {
        keyInterval = 500
    }

    // don't search for every key (especially relevant for bnumber)
    clearTimeout(typeTimer)
    typeTimer = setTimeout(function() { sendQuery(e.target.value); }, keyInterval)
});

// We load the options returned into an html string and then add them to the selectpicker at the end, to save A LOT of time.
function sendQuery(search_str) {
    $("#search").empty();
    $('#search').selectpicker("refresh");
    if (search_str.length >= 3) {
      $.ajax({
        type: "GET",
        url: "/main/search/" + encodeURIComponent(search_str),
        contentType: 'application/json',
        success: function(response) {
          let optionString = ""
          for (let key = 0; key < response.length; key++) {
            let username = response[key]['username'];
            let bnumber = response[key]['bnumber'];
            let firstName = response[key]['firstName'];
            let lastName = response[key]['lastName'];
            let type = response[key]['type'];
            if (type == "Student") {
              choice_text = bnumber + ': ' + firstName + ' ' + lastName;
              highlighted_text = highlight(choice_text, search_str) + `<small class='text-muted'>${username}</small>`;
              optionString += `<option value="${bnumber}" data-content="${highlighted_text}" data-subtext="${username}">${choice_text}</option>`;
            }
          }
          $("#search").append(createFragment(optionString))
          $('#search').selectpicker("refresh");
        }
      });
    }
}
