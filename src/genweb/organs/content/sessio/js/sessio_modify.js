$(document).ready(function(){
  "use strict";

  $('#sortable').sortable({
    placeholder: 'ui-state-highlight',
    opacity: 0.5,
    scroll: false,
    start: function(event, ui){
      start = ui.item.index();
    },
    update: function(event, ui){
      var params = {};
      params.itemid = ui.item.attr('id');
      params.action = 'movepunt';
      params.delta = ui.item.index() - start
      $.ajax({
        type: 'POST',
        url: '@@fcmoveTable',
        data: params,
        success: function(){
          setTimeout(() => window.location.reload(), 500);
        },
      });
    },
  }).disableSelection();

  $('.sortable2').sortable({
    placeholder: 'ui-state-highlight2',
    opacity: 0.5,
    scroll: false,
    start: function(event, ui){
      start = ui.item.index();
    },
    update: function(event, ui){
      var params = {};
      params.itemid = ui.item.attr('id');
      params.action = 'movesubpunt';
      params.delta = ui.item.index() - start
      $.ajax({
        type: 'POST',
        url: '@@fcmoveTable',
        data: params,
        success: function(){
          setTimeout(() => window.location.reload(), 500);
        },
      });
    },
  }).disableSelection();

  /*
  * LÓGICA DE SELECCIÓN DE PUNTO (PICKING)
  */
  function mouseHandler(e) {
    const currentLi = $(this);
    if (!currentLi.hasClass('picked')) {
      // Deseleccionar cualquier otro
      $('.ui-sortable li.picked').each(function(){
        $(this).removeClass('picked')
          .find('.einesSpan').toggleClass('d-none');
        $(this).find('.boleta').show();
      });
      // Seleccionar el actual
      currentLi.addClass('picked');
      currentLi.find('.einesSpan').toggleClass('d-none');
      currentLi.find('.boleta').hide();
    }
  }

  $('.ui-sortable li').on('click', mouseHandler);

  // Click fuera de la lista para deseleccionar
  $(window).on("click.Bst", function (event) {
    if ($(event.target).closest('.modal').length > 0) return; // No hacer nada si el click es en un modal
    if ($(event.target).closest('#sortable').length === 0) {
      $('.ui-sortable li.picked').each(function(){
        $(this).removeClass('picked')
          .find('.einesSpan').toggleClass('d-none');
        $(this).find('.boleta').show();
      });
    }
  });

  /*
  * MANEJO DE MODALES
  */
  // Limpiar formularios cuando se cierran los modales
  const $modalPunt = $('#modalPunt');
  if ($modalPunt.length) {
    $modalPunt.on('hidden.bs.modal', function(){
      const $title = $modalPunt.find('#new-punt-title');
      if ($title.length) $title.val('');
    });
  }

  const $modalAcord = $('#modalAcord');
  if ($modalAcord.length) {
    $modalAcord.on('hidden.bs.modal', function(){
      const $title = $modalAcord.find('#new-acord-title');
      if ($title.length) $title.val('');
    });
  }

  // Creación de Punts
  $('.createPunt').on('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    const value = $("#new-punt-title").val();
    if (!value || value.trim() === '') {
      alert('El títol no pot estar buit.');
      return;
    }
    $.ajax({
      type: 'POST',
      url: window.location.href.split('?')[0].replace(/\/$/, "") + '/@@createElement',
      data: { action: 'createPunt', name: value },
      success: function(){
        if ($modalPunt.length) $modalPunt.modal('hide');
        setTimeout(() => window.location.reload(), 500);
      },
      error: function(){
        alert('Hi ha hagut un error al crear el punt.');
      }
    });
  });

  // Creación de Acords
  $('.createAcord').on('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    const value = $("#new-acord-title").val();
    if (!value || value.trim() === '') {
      alert('El títol no pot estar buit.');
      return;
    }
    $.ajax({
      type: 'POST',
      url: window.location.href.split('?')[0].replace(/\/$/, "") + '/@@createElement',
      data: { action: 'createAcord', name: value },
      success: function(){
        if ($modalAcord.length) $modalAcord.modal('hide');
        setTimeout(() => window.location.reload(), 500);
      },
      error: function(){
        alert('Hi ha hagut un error al crear l\'acord.');
      }
    });
  });

  /*
  * MODAL DE CONFIRMACIÓN GENÉRICO (Bootstrap 5 way)
  */
  const $confirmModal = $('#modalConfirm');
  if ($confirmModal.length) {
    $confirmModal.on('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      const title = $(button).data('modal-title');
      const body = $(button).data('modal-body');
      const action = $(button).data('modal-action');

      $confirmModal.find('.modal-title').text(title);
      $confirmModal.find('.modal-body').text(body);

      const $confirmButton = $confirmModal.find('#modalConfirmButton');
      $confirmButton.off('click').on('click', function(){
        if (action === 'delete') {
          const itemId = $(button).data('item');
          const itemType = $(button).data('type');
          const itemUrl = $(button).data('url');
          deleteElement(itemUrl, itemId, itemType);
        } else if (action === 'hideAgreement') {
          const url = $(button).data('item');
          hideAgreement(url);
        }
        $confirmModal.modal('hide');
      });
    });
  }

  /*
  * EDICIÓN DE TÍTULOS
  */
  const $editTitleModalEl = $('#modalEditTitle');
  if ($editTitleModalEl.length) {
    // Delegación de eventos para los botones de editar
    $('#sortable').on('click', '.edit, .edit2, a.editTitle', function (e) {
      e.preventDefault();
      e.stopPropagation();
      const pk = $(this).data('id');
      const currentTitle = $(this).is('a') ? $(this).text().trim() : $(this).data('title');
      $('#edit-title-input').val(currentTitle);
      $('#edit-title-pk').val(pk);
      $editTitleModalEl.modal('show');
    });

    $('#saveTitleButton').on('click', function(){
      const pk = $('#edit-title-pk').val();
      const newTitle = $('#edit-title-input').val();
      if (!newTitle) {
        alert('El títol no pot estar buit.');
        return;
      }
      $.ajax({
        url: $(this).data('url') + '/changeTitle',
        type: 'POST',
        data: { pk: pk, value: newTitle },
        success: function(){
          $('a.editTitle[data-id="' + pk + '"]').text(newTitle);
          $('button.edit[data-id="' + pk + '"], button.edit2[data-id="' + pk + '"]').data('title', newTitle);
          $editTitleModalEl.modal('hide');
        },
        error: function(){
          alert('Hi ha hagut un error al desar el títol.');
        }
      });
    });
  }

  /*
  * ESTADOS DE PUNTO (COLOR + TEXTO)
  */
  $("li.defaultValue").on('click', function(){
    const colorSelected = $(this).find('.bi-circle-fill').css('color');
    const $buttonGroup = $(this).closest('.btn-group');
    $buttonGroup.find('.bullet-toggle > i').css({ 'color': colorSelected });
    $buttonGroup.closest('.einesSpan').parent().find('.boleta > span > i').css({ 'color': colorSelected });

    const textSelected = $(this).find('span').text();
    $buttonGroup.closest('.einesSpan').parent().find('.boleta > span > span').text(textSelected);
  });

  /*
  * IMPORTACIÓN MASIVA DE PUNTOS Y ACUERDOS
  */
  $('#importPointsButton').on('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    const content = $("#manual-import-text").val();
    if (!content || content.trim() === '') {
      alert('El contingut no pot estar buit.');
      return;
    }

    // Crear un formulario temporal para enviar los datos
    const $form = $('<form>', {
      'method': 'POST',
      'action': window.location.href.split('?')[0].replace(/\/$/, "") + '/manualStructureCreation'
    });

    $form.append($('<input>', {
      'type': 'hidden',
      'name': 'form.widgets.message',
      'value': content
    }));

    $form.append($('<input>', {
      'type': 'hidden',
      'name': 'form.buttons.send',
      'value': 'Send'
    }));

    // No CSRF token añadido

    $('body').append($form);
    $form.submit();
  });

  // Limpiar el textarea cuando se cierra el modal de importación
  const $modalPunts = $('#modalPunts');
  if ($modalPunts.length) {
    $modalPunts.on('hidden.bs.modal', function(){
      const $textarea = $modalPunts.find('#manual-import-text');
      if ($textarea.length) $textarea.val('');
    });
  }
});

/*
 * FUNCIONES GLOBALES (usadas en los manejadores de eventos)
 */
function hideAgreement(url){
  $.ajax({
    type: 'POST',
    url: url + '/hideAgreement',
    success: function(){
      setTimeout(() => window.location.reload(), 500);
    }
  });
}

function deleteElement(url, name, portal_type){
  const id = CSS.escape(name);
  $.ajax({
    type: 'POST',
    url: url + '/deleteElement',
    data: { action: 'delete', id: name, type: portal_type },
    success: function(){
      setTimeout(() => window.location.reload(), 500);
    }
  });
}