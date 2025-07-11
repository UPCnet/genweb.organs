document.addEventListener('DOMContentLoaded', function(){
  "use strict";
  let refreshNeeded = false;

  $(document).ajaxStop(function(){
    if (refreshNeeded) { setTimeout(() => window.location.reload(), 500); }
  });

  $(".addQuorum").on('click', function(){
    $.post($(this).data('url') + '/addQuorum', () => { refreshNeeded = true; }); 
  });
});