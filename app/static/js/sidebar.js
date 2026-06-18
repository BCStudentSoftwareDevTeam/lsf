$(document).ready(function() {
  let userAgentString = navigator.userAgent;
  // Detect Chrome
  let chromeAgent = userAgentString.indexOf("Chrome") > -1;
  if (chromeAgent) {
    $('.navbar a').removeAttr('tabindex');
    $('.navbar li').removeAttr('tabindex');
    $('.navbar div').removeAttr('tabindex');
    }
  $('#sidebar-toggle').on('click', function() {
    if ($('#sidebar').hasClass('sidebar-open')) {
      closeSidebar();
    } else {
      openSidebar();
    }
  });
  $('#sidebar-overlay').on('click', function() {
    closeSidebar();
  });
  // Change the text of the admin-toggle pannel when the user clicks on it to the change unicode character.
  $('#admin-toggle').on('click', function() {
    if ($('#admin').hasClass('in')) { //Check if its class in or colapse in
      toggleAdminPanelClose();
    } else {
      toggleAdminPanelOpen();
    }
  });
  });

function openSidebar() {
  $('#sidebar').addClass('sidebar-open');
  $('#sidebar-overlay').addClass('active');
  $('body').addClass('sidebar-is-open');
  $('#sidebar-toggle').attr('aria-expanded', true);
}
function closeSidebar() {
  $('#sidebar').removeClass('sidebar-open');
  $('#sidebar-overlay').removeClass('active');
  $('body').removeClass('sidebar-is-open');
  $('#sidebar-toggle').attr('aria-expanded', false);
}
// Change the text of the admin-toggle pannel when the user clicks on it to the open unicode character.
function toggleAdminPanelOpen() {
  $('#admin-toggle h4').html('Administration ⯅');
}
// Change the text of the admin-toggle pannel when the user clicks on it to the close unicode character.
function toggleAdminPanelClose() {
  $('#admin-toggle h4').html('Administration ⯆');
}
