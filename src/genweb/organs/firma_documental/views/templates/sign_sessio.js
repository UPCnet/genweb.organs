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

  // Funcionalidad checks
  function hideConfirmButtonIfNoFiles(hide = false) {
    const selected = $('input:checked').length > 0;
    if (hide) $('.btn-send-confirm').toggle(selected);
    else $('.btn-send-confirm').prop('disabled', !selected);
  }

  hideConfirmButtonIfNoFiles(true);

  $('.form-check-input').change(function () {
    const uuid = $(this).attr('name').substring(6); // quitar el 'check:' del nombre del checkbox
    const checked = $(this).is(':checked');
    // desactivar/activar la visualización del documento
    $('#' + uuid).toggle(checked);
    let active = checked;
    function hasCheckedFilesCallback() {
      if ($('.form-check-input[name="check:' + this.id + '"]').is(':checked')) {
        active = true;
        return false;
      }
    }
    // comprobar si hay algún documento activo en el subpunt
    if (!active) {
      $('#' + uuid).siblings('.filesinTable').each(hasCheckedFilesCallback);
    }
    // desactivar/activar la visualización del subpunt (no se verá si ninguno de sus documentos está activo)
    // no tendrá efecto si es un documento que está directamente en el punt
    // Nota: .li_subgrups tiene un !important en el display
    //       asi que no hay más remedio que poner el estilo manualmente para esconder el elemento
    if (!active) $('#' + uuid).parents("ol.li_subgrups").attr('style', 'display:none !important')
    else $('#' + uuid).parents("ol.li_subgrups").removeAttr('style')
    //# desactivar el nodo que contiene todos los ficheros, solo funcionará en el punt
    $('#' + uuid).parents(".listFiles").parent().toggle(active);
    // obtener el punt a partir del documento dentro de un subpunt
    let puntTitle = $('#' + uuid).parents(".container-subpunts").siblings(".puntTitle");
    if (puntTitle.length == 0) {
      // si no encuentra desde el subpunt es que es un documento que está diractamente en el punt
      puntTitle = $('#' + uuid).parents(".puntTitle");
    }
    // comprobar si hay algún subpunt activo en el punt
    if (!active) {
      puntTitle.siblings(".container-subpunts").children("ol.li_subgrups").find(".filesinTable").each(hasCheckedFilesCallback);
    }
    // en caso de que no haya ningún subpunt activo en el punt, comprobar si hay algún documento activo en el punt
    if (!active) {
      puntTitle.find(".filesinTable").each(hasCheckedFilesCallback);
    }
    // desactivar/activar la visualización del punt (no se verá si ninguno de sus documentos o subpunts está activo)
    puntTitle.parents("li").toggle(active);

    // comprobar si hay algún documento seleccionado en la lista de documentos.
    // en caso de que no haya ninguno, se oculta el botón que abre la modal de confirmación
    hideConfirmButtonIfNoFiles();
  });

  // Enviar ficheros seleccionados a firmar
  $('#send-sign-btn').click(function () {
    $('#send-confirmation').modal('hide');
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
});