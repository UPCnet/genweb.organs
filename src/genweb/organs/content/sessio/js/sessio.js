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


  $("#expandAll").click(function(){
    // $(".expand").parent().parent().parent().slideDown();
    // $(".expand").hide();
    // $(".notexpand").show();
    // $(".expand").parent().parent().parent().find('.sortable2').slideDown();
    // $(".expand").parent().parent().parent().find('.listFiles').slideDown();
    $("#expandAll").toggleClass('d-none');
    $("#collapseAll").toggleClass('d-none');
  });

  $("#collapseAll").click(function(){
    // $(".notexpand").slideUp();
    // $(".notexpand").hide();
    // $(".expand").show();
    // $(".expand").parent().parent().parent().find('.sortable2').slideUp();
    // $(".expand").parent().parent().parent().find('.listFiles').slideUp();
    $("#expandAll").toggleClass('d-none');
    $("#collapseAll").toggleClass('d-none');
  });

  // Para el desplegable de información de voto público
  $(".openInfo").click(function () {
    const toggleVoteInfo = $(this).data("open");
    $(toggleVoteInfo).toggleClass("d-none");
    $(this).find(".bi-chevron-down").toggleClass("d-none");
    $(this).find(".bi-chevron-up").toggleClass("d-none");
  });
  


});