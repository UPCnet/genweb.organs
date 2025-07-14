$(document).ready(function() {
  "use strict";

  function voteHandler(type) {
    return function() {
      $.ajax({
        type: 'POST',
        url: $(this).attr('data-id') + '/' + type + 'Vote',
        success: function(result) {
          result = JSON.parse(result);
          if (result.status !== "success") {
            alert(result.msg);
          }
          refreshNeeded = true;
        },
      });
    };
  }

  $(".btn-notvote.favor").on('click', voteHandler('favor'));
  $(".btn-notvote.against").on('click', voteHandler('against'));
  $(".btn-notvote.white").on('click', voteHandler('white'));
});