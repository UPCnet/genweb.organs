$(document).ready(function(){
  "use strict";

  let refreshNeeded = false;

  $(document).ajaxStop(function(){
    if (refreshNeeded) { setTimeout(() => window.location.reload(), 500); }
  });

  // Para el desplegable de información de voto público
  //$(".openInfo").click(function () {
  //  $(this).toggleClass("opened");
  //  $($(this).attr("data-open")).toggleClass("opened");
  //});
});