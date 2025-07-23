$(document).ready(function() {
  "use strict";

  function voteHandler(type) {
    return function() {
      $.ajax({
        type: 'POST',
        url: $(this).data('id') + '/' + type + 'Vote',
        success: function(result) {
          if (result.status !== "success") {
            alert(result.msg);
          }
          setTimeout(() => window.location.reload(), 500);
        },
      });
    };
  }

  $(".btn-notvote.favor").on('click', voteHandler('favor'));
  $(".btn-notvote.against").on('click', voteHandler('against'));
  $(".btn-notvote.white").on('click', voteHandler('white'));
});