$(document).ready(function(){

    /*
    * ESTADOS DE PUNTO (COLOR)
    */
    $("li.defaultValue").on('click', function(){
      const colorSelected = $(this).find('.bi-circle-fill').css('color');
      const $buttonGroup = $(this).closest('.btn-group');
      $buttonGroup.find('.bullet-toggle > i').css({ 'color': colorSelected });
      $('#collapse-' + $buttonGroup.parent().find('a').data('id') + ' button.bullet-toggle > i').css({ 'color': colorSelected });
    });
  });