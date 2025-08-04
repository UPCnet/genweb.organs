
// Preview Acta
var $btnPreview = $('#previewActaBtn');
if ($btnPreview.length) {
  $btnPreview.on('click', function (e) {
    e.preventDefault();
    var url = $btnPreview.data('url');
    $.ajax({
      url: url,
      xhrFields: { withCredentials: true },
      success: function (html) {
        $('#previewActaBody').html(html);
        var modalEl = $('previewActaModal');
        var modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
      }
    });
  });
}

// Print Acta
var $btnPrint = $('#printActaBtn');
var $iframe = $('#printActaIframe');
if ($btnPrint.length && $iframe.length) {
  $btnPrint.on('click', function (e) {
    e.preventDefault();
    var url = $btnPrint.data('url');
    $iframe.attr('src', url + '/printActa');
    $iframe.off('load').on('load', function () {
      setTimeout(function () {
        $iframe[0].contentWindow.focus();
        $iframe[0].contentWindow.print();
      }, 200);
    });
  });
}