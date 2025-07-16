$(document).ready(function(){
  "use strict";

  $(".openQuorum").on('click', function(){ 
    $.post($(this).data('url') + '/openQuorum', () => { setTimeout(() => window.location.reload(), 500); }); 
  });

  $(".closeQuorum").on('click', function(){
    $.post($(this).data('url') + '/closeQuorum', () => { setTimeout(() => window.location.reload(), 500); }); 
  });
});