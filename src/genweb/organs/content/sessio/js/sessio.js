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

  $(".btn-expand-collapse").click(function(){
    $(this).find(".bi-chevron-down, .bi-chevron-up").toggleClass('d-none');
  });

  $("#expandAll").click(function(){
    $(".btn-expand-collapse.collapsed").click();
    $(".btn-expand-collapse.collapsed .bi-chevron-down, .btn-expand-collapse.collapsed .bi-chevron-up").toggleClass('d-none');
    $("#expandAll, #collapseAll").toggleClass('d-none');
  });

  $("#collapseAll").click(function(){
    $(".btn-expand-collapse:not(.collapsed)").click();
    $(".btn-expand-collapse:not(.collapsed) .bi-chevron-down, .btn-expand-collapse:not(.collapsed) .bi-chevron-up").toggleClass('d-none');
    $("#expandAll, #collapseAll").toggleClass('d-none');
  });

  // Para el desplegable de información de voto público
  $(".openInfo").click(function () {
    const toggleVoteInfo = $(this).data("open");
    $(toggleVoteInfo).toggleClass("d-none");
    $(this).find(".bi-chevron-down").toggleClass("d-none");
    $(this).find(".bi-chevron-up").toggleClass("d-none");
  });
});