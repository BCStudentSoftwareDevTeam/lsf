$(document).ready(function() {
  let userAgentString = navigator.userAgent;
  // Detect Chrome
  let chromeAgent = userAgentString.indexOf("Chrome") > -1;
  if (chromeAgent) {
    $('.navbar a').removeAttr('tabindex');
    $('.navbar li').removeAttr('tabindex');
    $('.navbar div').removeAttr('tabindex');
    }

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
});
