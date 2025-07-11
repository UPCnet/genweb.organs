document.addEventListener('DOMContentLoaded', function(){
  "use strict";
  let refreshNeeded = false;

  $(document).ajaxStop(function(){
    if (refreshNeeded) { setTimeout(() => window.location.reload(), 500); }
  });

  $(".openQuorum").on('click', function(){ 
    $.post($(this).data('url') + '/openQuorum', () => { refreshNeeded = true; }); 
  });

  $(".closeQuorum").on('click', function(){
    $.post($(this).data('url') + '/closeQuorum', () => { refreshNeeded = true; }); 
  });
});