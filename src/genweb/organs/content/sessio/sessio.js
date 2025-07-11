document.addEventListener('DOMContentLoaded', function() {
  "use strict";
  const $ = jQuery;
  let refreshNeeded = false;

  $(document).ajaxStop(function () {
    if (refreshNeeded) {
      window.location.reload();
    }
  });

  // Para el desplegable de información de voto público
  $(".openInfo").click(function () {
    $(this).toggleClass("opened");
    $($(this).attr("data-open")).toggleClass("opened");
  });
});