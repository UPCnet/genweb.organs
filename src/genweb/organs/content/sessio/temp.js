<script type="text/javascript" tal:condition="canModify">
                // Script unificado para la página de sesión
                document.addEventListener('DOMContentLoaded', function () {
                    "use strict";

                    let refreshNeeded = false;
                    const $ = jQuery; // Para mantener la compatibilidad con el código existente.

                    // Recargar la página si es necesario después de una llamada AJAX
                    $(document).ajaxStop(function () {
                        if (refreshNeeded) {
                            // Usamos un pequeño retardo para asegurar que el servidor ha procesado todo
                            setTimeout(() => window.location.reload(), 500);
                        }
                    });

                    /*
                    * MANEJO DE MODALES
                    */

                    // Limpiar formularios cuando se cierran los modales
                    const modalPunt = document.getElementById('modalPunt');
                    if(modalPunt) {
                        modalPunt.addEventListener('hidden.bs.modal', () => {
                            const title = modalPunt.querySelector('#new-punt-title');
                            if(title) title.value = '';
                        });
                    }

                    const modalAcord = document.getElementById('modalAcord');
                    if(modalAcord) {
                        modalAcord.addEventListener('hidden.bs.modal', () => {
                            const title = modalAcord.querySelector('#new-acord-title');
                            if(title) title.value = '';
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
              success: function () {
                                const modal = bootstrap.Modal.getInstance(modalPunt);
                                if (modal) modal.hide();
                                refreshNeeded = true;
                            },
                            error: function() {
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
                            success: function () {
                                const modal = bootstrap.Modal.getInstance(modalAcord);
                                if (modal) modal.hide();
                                refreshNeeded = true;
                            },
                            error: function() {
                                alert('Hi ha hagut un error al crear l\'acord.');
                            }
                        });
                    });

                    /*
                    * MODAL DE CONFIRMACIÓN GENÉRICO (Bootstrap 5 way)
                    */
                    const confirmModal = document.getElementById('modalConfirm');
                    if (confirmModal) {
                        confirmModal.addEventListener('show.bs.modal', event => {
                            const button = event.relatedTarget; // Botón que disparó el modal
                            // Extraer información de los atributos data-*
                            const title = button.getAttribute('data-modal-title');
                            const body = button.getAttribute('data-modal-body');
                            const action = button.getAttribute('data-modal-action');

                            confirmModal.querySelector('.modal-title').textContent = title;
                            confirmModal.querySelector('.modal-body').textContent = body;

                            const confirmButton = confirmModal.querySelector('#modalConfirmButton');

                            // Limpiamos eventos anteriores para evitar ejecuciones múltiples
                            $(confirmButton).off('click').on('click', function() {
                                if (action === 'delete') {
                                    const itemId = button.getAttribute('data-item');
                                    const itemType = button.getAttribute('data-type');
                                    deleteElement(itemId, itemType);
                                } else if (action === 'hideAgreement') {
                                    const url = button.getAttribute('data-item-url');
                                    hideAgreement(url);
                                }
                                bootstrap.Modal.getInstance(confirmModal).hide();
                            });
                        });
                    }


                    /*
                    * EDICIÓN DE TÍTULOS
                    */
                    const editTitleModalEl = document.getElementById('modalEditTitle');
                    if (editTitleModalEl) {
                        const editTitleModal = new bootstrap.Modal(editTitleModalEl);
                        // Delegación de eventos para los botones de editar
                        $('#sortable').on('click', '.edit, .edit2, a.editTitle', function(e) {
                            e.preventDefault();
              e.stopPropagation();
                            const pk = $(this).data('id');
                            const currentTitle = $(this).is('a') ? $(this).text().trim() : $(this).data('title');
                            $('#edit-title-input').val(currentTitle);
                            $('#edit-title-pk').val(pk);
                            editTitleModal.show();
                        });

                        $('#saveTitleButton').on('click', function() {
                            const pk = $('#edit-title-pk').val();
                            const newTitle = $('#edit-title-input').val();
                            if (!newTitle) {
                                alert('El títol no pot estar buit.');
                                return;
                            }
                            $.ajax({
                                url: 'changeTitle',
                                type: 'POST',
                                data: { pk: pk, value: newTitle },
                                success: function() {
                                    $('a.editTitle[data-id="' + pk + '"]').text(newTitle);
                                    $('button.edit[data-id="' + pk + '"], button.edit2[data-id="' + pk + '"]').data('title', newTitle);
                                    editTitleModal.hide();
                                },
                                error: function() {
                                    alert('Hi ha hagut un error al desar el títol.');
                }
              });
            });
                    }

                    /*
                    * LÓGICA DE SELECCIÓN DE PUNTO (PICKING)
                    */
                    function mouseHandler(e) {
                        const currentLi = $(this);
                        if (!currentLi.hasClass('picked')) {
                            // Deseleccionar cualquier otro
                            $('.ui-sortable li.picked').each(function() {
                                $(this).removeClass('picked')
                                    .find('.einesSpan, .show').toggleClass('einesSpan show');
                                $(this).find('.boleta').show();
                            });
                            // Seleccionar el actual
                            currentLi.addClass('picked');
                            currentLi.find('.einesSpan').toggleClass('einesSpan show');
                            currentLi.find('.boleta').hide();
                        }
                    }

                    $('.ui-sortable li').on('click', mouseHandler);

                    // Click fuera de la lista para deseleccionar
                    $(window).on("click.Bst", function (event) {
                        if ($(event.target).closest('.modal').length > 0) return; // No hacer nada si el click es en un modal
                        if ($(event.target).closest('#sortable').length === 0) {
                             $('.ui-sortable li.picked').each(function() {
                                $(this).removeClass('picked')
                                    .find('.einesSpan, .show').toggleClass('einesSpan show');
                                $(this).find('.boleta').show();
                            });
                        }
                    });


                    /*
                    * ESTADOS DE PUNTO (COLOR)
                    */
            $("li.defaultValue").on('click', function () {
                        const colorSelected = $(this).find('.bi-circle-fill').css('color');
                        const $buttonGroup = $(this).closest('.btn-group');
                        $buttonGroup.find('.bullet-toggle > i').css({ 'color': colorSelected });
                        $buttonGroup.closest('.einesSpan').parent().find('.boleta > span > i').css({ 'color': colorSelected });
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
                        const form = $('<form>', {
                            'method': 'POST',
                            'action': window.location.href.split('?')[0].replace(/\/$/, "") + '/manualStructureCreation'
                        });

                        form.append($('<input>', {
                            'type': 'hidden',
                            'name': 'form.widgets.message',
                            'value': content
                        }));

                        form.append($('<input>', {
                            'type': 'hidden',
                            'name': 'form.buttons.send',
                            'value': 'Send'
                        }));

                        // No CSRF token añadido

                        $('body').append(form);
                        form.submit();
                    });

                    // Limpiar el textarea cuando se cierra el modal de importación
                    const modalPunts = document.getElementById('modalPunts');
                    if(modalPunts) {
                        modalPunts.addEventListener('hidden.bs.modal', () => {
                            const textarea = modalPunts.querySelector('#manual-import-text');
                            if(textarea) textarea.value = '';
                        });
                    }
                });

                /*
                * FUNCIONES GLOBALES (usadas en los manejadores de eventos)
                */
                function hideAgreement(url) {
                    jQuery.ajax({
              type: 'POST',
                        url: url + '/hide-agreement',
                        success: function() { window.location.reload(); },
                        error: function() { alert('Error en l\'operació'); }
                    });
                }

                function deleteElement(name, portal_type) {
                    const id = CSS.escape(name);
                    jQuery.ajax({
              type: 'POST',
                        url: window.location.href.split('?')[0].replace(/\/$/, "") + '/deleteElement',
                        data: { action: 'delete', id: name, type: portal_type },
                        success: function(){
                            jQuery('#' + id).fadeOut('slow', function() { $(this).remove(); });
                        },
                        error: function() {
                            alert('Error on deleting element');
                            window.location.reload();
                        }
                    });
                }
        </script>

      <div style="margin-bottom:20px;"></div>

      <script type="text/javascript" tal:condition="canViewManageVote">
                document.addEventListener('DOMContentLoaded', function () {
                    "use strict";
                    let refreshNeeded = false;
                    const $ = jQuery;

                    $(document).ajaxStop(function () {
                        if (refreshNeeded) { setTimeout(() => window.location.reload(), 500); }
                    });

        $(".reopenVote").on('click', function () {
          $.ajax({
            type: 'POST',
            url: $(this).attr('data-url') + '/reopenVote',
            success: function (result) {
                                result = JSON.parse(result);
                                if (result.status !== "success") { alert(result.msg); }
              refreshNeeded = true;
            },
          });
        });

        $(".removeVote").on('click', function () {
                        // Este modal ahora lo gestiona el sistema genérico
                    });

                    $(".closeVote, .recloseVote").on('click', function () {
          $.ajax({
            type: 'POST',
            url: $(this).attr('data-id') + '/closeVote',
                            success: function () { refreshNeeded = true; },
          });
        });

        $(".openPublicVote").on('click', function () {
          $.ajax({
            type: 'POST',
            url: $(this).attr('data-id') + '/openPublicVote',
                            success: function () { refreshNeeded = true; },
          });
        });

        $(".openOtherPublicVote").on('click', function () {
          let titolVotacio = prompt($(this).attr('data-title'), "");
          if (titolVotacio && confirm('T\u00edtol: ' + titolVotacio + '\n\nEst\xE0s segur que vols obrir aquesta esmena?')) {
            $.ajax({
              type: 'POST',
              data: { 'title': titolVotacio },
              url: $(this).attr('data-id') + '/openOtherPublicVote',
                                success: function () { refreshNeeded = true; },
            });
          }
        });

        $(".refreshVote").on('click', function () {
                        const uid = $(this).attr('data-uid');
          $.ajax({
            type: 'GET',
            data: { 'UID': uid },
            url: 'reloadVoteStats',
            success: function (result) {
                                const data = $.parseJSON(result);
                                const voteRow = $('#vote-' + uid);
                                const infoRow = $('#' + uid);

                                voteRow.find('.vote-totalVote').html(data.totalVote);
                                infoRow.find('.vote-users-totalVote').html(data.totalVoteListHTML);
                                voteRow.find('.vote-state').html(data.state);

                                const infoIcon = voteRow.find('.bi-info-circle');
              if (data.open) {
                                    infoIcon.attr('title', 'Inici: ' + data.hourOpen);
              } else {
                                    voteRow.find('.vote-favorVote').html(data.favorVote);
                                    voteRow.find('.vote-againstVote').html(data.againstVote);
                                    voteRow.find('.vote-whiteVote').html(data.whiteVote);
                                    infoRow.find('.vote-users-favorVote').html(data.favorVoteListHTML);
                                    infoRow.find('.vote-users-againstVote').html(data.againstVoteListHTML);
                                    infoRow.find('.vote-users-whiteVote').html(data.whiteVoteListHTML);
                                    infoIcon.attr('title', 'Inici: ' + data.hourOpen + '\nFi: ' + data.hourClose);
                                    voteRow.find('.refreshVote').remove();
              }
            },
          });
        });
                });
      </script>

      <script type="text/javascript" tal:condition="canViewVoteButtons">
                document.addEventListener('DOMContentLoaded', function () {
                    "use strict";
                    let refreshNeeded = false;
                    const $ = jQuery;

                    $(document).ajaxStop(function () {
                        if (refreshNeeded) { setTimeout(() => window.location.reload(), 500); }
                    });

                    function voteHandler(type) {
                        return function() {
          $.ajax({
            type: 'POST',
                                url: $(this).attr('data-id') + '/' + type + 'Vote',
            success: function (result) {
                                    result = JSON.parse(result);
                                    if (result.status !== "success") { alert(result.msg); }
                refreshNeeded = true;
            },
          });
                        };
                    }

                    $(".btn-notvote.favor").on('click', voteHandler('favor'));
                    $(".btn-notvote.against").on('click', voteHandler('against'));
                    $(".btn-notvote.white").on('click', voteHandler('white'));
                });
      </script>









            <script type="text/javascript" tal:condition="python: canViewManageQuorumButtons or canViewAddQuorumButtons">
                document.addEventListener('DOMContentLoaded', function () {
                    "use strict";
                    let refreshNeeded = false;
                    const $ = jQuery;

                    $(document).ajaxStop(function () {
                        if (refreshNeeded) { setTimeout(() => window.location.reload(), 500); }
                    });

                    $(".openQuorum").on('click', function () { $.post('openQuorum', () => { refreshNeeded = true; }); });
                    $(".closeQuorum").on('click', function () { $.post('closeQuorum', () => { refreshNeeded = true; }); });
                    $(".addQuorum").on('click', function () { $.post('addQuorum', () => { refreshNeeded = true; }); });
                });
      </script>








            <script type="text/javascript">
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
      </script>