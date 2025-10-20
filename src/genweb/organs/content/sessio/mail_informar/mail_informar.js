$(document).ready(function(){
  $('a[data-target="#informarModal"]').on('click', function(e) {
    e.preventDefault();
    var url = $(this).attr('href');
    $.ajax({
      url: url,
      xhrFields: { withCredentials: true },
      success: function (html) {
        $('#informarModal .modal-body').html(html);
        var modalEl = $('#informarModal');
        var modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
      }
    });
  });
});
