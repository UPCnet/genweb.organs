$(document).ready(function(){
  "use strict";

  $(".addQuorum").on('click', function(){
    $.post($(this).data('url') + '/addQuorum', () => { refreshNeeded = true; }); 
  });
});