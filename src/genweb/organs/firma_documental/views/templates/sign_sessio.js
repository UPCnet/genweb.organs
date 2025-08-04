$(document).ready(function(){
  "use strict";

  $('#signActa').on('click', function(){
    $('.spinner-block').removeClass('d-none');
    $.ajax({
      url: $(this).attr('data-sign-url'),
      type: 'POST',
      success: function(data){
        window.location.reload();
      },
      error: function(){
        window.location.reload();
      }
    })
  });

  $('#send-sign-btn').click(function () {
    $('#previewDocModal').modal('hide');
    var data = {};
    $('input:checked').each(function () {
      data[this.name] = this.value;
    });
    $('.spinner-block').removeClass('d-none');
    $.ajax({
      url: 'uploadFiles',
      type: 'POST',
      data: data,
      contentType: 'application/x-www-form-urlencoded; charset=utf-8',
    }).then(() => window.location.reload());
  });

  // Preview documentacio
  var $btnPreviewDoc = $('#previewDocBtn');
  if ($btnPreviewDoc.length) {
    $btnPreviewDoc.on('click', function (e) {
      e.preventDefault();
      var modalEl = $('#previewDocModal');
      var modal = bootstrap.Modal.getOrCreateInstance(modalEl);
      modal.show();
    });
  }

});