
                  <script type="text/javascript">
                    $('#signActa').on('click', function(){
                      $('#infoSend').show();
                      $('#miniLoaderScreen').show();
                      $.ajax({
                        url: $(this).attr('data-sign-url'),
                        type: 'POST',
                        success: function(data){
                          $('#miniLoaderScreen').hide();
                          $('#infoSend').hide();
                          window.location.reload();
                        },
                        error: function(){
                          $('#miniLoaderScreen').hide();
                          $('#infoSend').hide();
                          window.location.reload();
                        }
                      })
                      $('#ajax-spinner').hide();
                    });
                  </script>


<script type="text/javascript">
              $(function () {

                function hideConfirmButtonIfNoFiles(hide = false) {
                  selected = $('input:checked').length > 0;
                  if (hide) $('.btn-send-confirm').toggle(selected);
                  else $('.btn-send-confirm').prop('disabled', !selected);
                }
                hideConfirmButtonIfNoFiles(true);
                $('.expand').hide()
                $('.expand').click(function (e) {
                  e.stopPropagation();
                  $(this).hide();
                  $(this).siblings('.notexpand').show();
                  $(this).parents(".puntTitle").siblings('.sortable2').slideDown();
                  $(this).parents(".puntTitle").find('.listFiles').slideDown();
                });
                $('.notexpand').click(function (e) {
                  e.stopPropagation();
                  $(this).hide();
                  $(this).siblings('.expand').show();
                  $(this).parents(".puntTitle").siblings('.sortable2').slideUp();
                  $(this).parents(".puntTitle").find('.listFiles').slideUp();
                });
                /* $("#expandAll").hide()
                $("#expandAll").click(function () {
                  $(".expand").click();
                  $("#expandAll").hide();
                  $("#collapseAll").show();
                });
                $("#collapseAll").click(function () {
                  $(".notexpand").click();
                  $("#expandAll").show();
                  $("#collapseAll").hide();
                }); */
                $('.btn-send-confirm').click(function (e) { $('#send-confirmation').modal('show'); })
                $(':checkbox').change(function () {
                  const uuid = $(this).attr('name').substring(6); // quitar el 'check:' del nombre del checkbox
                  const checked = $(this).is(':checked');
                  // desactivar/activar la visualización del documento
                  $('#' + uuid).toggle(checked);
                  let active = checked;
                  function hasCheckedFilesCallback() {
                    if ($(':checkbox[name="check:' + this.id + '"]').is(':checked')) {
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
                  let puntTitle = $('#' + uuid).parents(".sortable2").siblings(".puntTitle");
                  if (puntTitle.length == 0) {
                    // si no encuentra desde el subpunt es que es un documento que está diractamente en el punt
                    puntTitle = $('#' + uuid).parents(".puntTitle");
                  }
                  // comprobar si hay algún subpunt activo en el punt
                  if (!active) {
                    puntTitle.siblings(".sortable2").children("ol.li_subgrups").find(".filesinTable").each(hasCheckedFilesCallback);
                  }
                  // en caso de que no haya ningún subpunt activo en el punt, comprobar si hay algún documento activo en el punt
                  if (!active) {
                    puntTitle.find(".filesinTable").each(hasCheckedFilesCallback);
                  }
                  // desactivar/activar la visualización del punt (no se verá si ninguno de sus documentos o subpunts está activo)
                  puntTitle.parent("li").toggle(active);

                  // comprobar si hay algún documento seleccionado en la lista de documentos.
                  // en caso de que no haya ninguno, se oculta el botón que abre la modal de confirmación
                  hideConfirmButtonIfNoFiles();
                });
                $('#send-sign-btn').click(function () {
                  $('#send-confirmation').modal('hide');
                  var data = {};
                  $('input:checked').each(function () {
                    data[this.name] = this.value;
                  });
                  $('#miniLoaderScreen').show();
                  $.ajax({
                    url: 'uploadFiles',
                    type: 'POST',
                    data: data,
                    contentType: 'application/x-www-form-urlencoded; charset=utf-8',
                  }).then(() => window.location.reload());
                });
              });
            </script>



                  <script type="text/javascript">
                    function printPage(newWindow){
                      newWindow.focus('printActa');
                      newWindow.print('printActa');
                    }
                  </script>