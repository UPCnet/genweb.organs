$(document).ready(function(){
  "use strict";

  $(".openQuorum").on('click', function(){ 
    $.post($(this).data('url') + '/openQuorum', () => { refreshNeeded = true; }); 
  });

  $(".closeQuorum").on('click', function(){
    $.post($(this).data('url') + '/closeQuorum', () => { refreshNeeded = true; }); 
  });
});