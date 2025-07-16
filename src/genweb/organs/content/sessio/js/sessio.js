$(document).ready(function(){
  "use strict";

  // Print Acta
  var $btnPrint = $('#printButlletiBtn');
  var $iframe = $('#printButlletiIframe');
  if ($btnPrint.length && $iframe.length) {
    $btnPrint.on('click', function (e) {
      e.preventDefault();
      var url = $btnPrint.data('url');
      $iframe.attr('src', url + '/butlleti');
      $iframe.off('load').on('load', function () {
        setTimeout(function () {
          $iframe[0].contentWindow.focus();
          $iframe[0].contentWindow.print();
        }, 200);
      });
    });
  }

  // Para el desplegable de información de voto público
  //$(".openInfo").click(function () {
  //  $(this).toggleClass("opened");
  //  $($(this).attr("data-open")).toggleClass("opened");
  //});
});