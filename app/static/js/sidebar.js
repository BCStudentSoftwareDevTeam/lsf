$(document).ready(function() {
  let userAgentString = navigator.userAgent;
  // Detect Chrome
  let chromeAgent = userAgentString.indexOf("Chrome") > -1;
  if (chromeAgent) {
    $('.navbar a').removeAttr('tabindex');
    $('.navbar li').removeAttr('tabindex');
    $('.navbar div').removeAttr('tabindex');
    }
  });
