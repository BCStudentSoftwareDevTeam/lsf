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
  $('#admin-toggle').on('click', function() {
    if ($('#admin').hasClass('in')) { 
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
function toggleAdminPanelOpen() {
  $('#admin-toggle h4 i').removeClass('bi-chevron-down').addClass('bi-chevron-up');
}
function toggleAdminPanelClose() {
  $('#admin-toggle h4 i').removeClass('bi-chevron-up').addClass('bi-chevron-down');
}
