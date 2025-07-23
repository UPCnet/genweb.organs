$(document).ready(function(){
  "use strict";

  $(".reopenVote").on('click', function(){
    $.ajax({
      type: 'POST',
      url: $(this).data('url') + '/reopenVote',
      success: function (result) {
        result = JSON.parse(result);
        if (result.status !== "success") { alert(result.msg); }
        setTimeout(() => window.location.reload(), 500);
      },
    });
  });

  $(".removeVote").on('click', function(){
    if(confirm("Est\u00e0s segur de voler eliminar la votaci\u00f3?")){
      $.ajax({
        type: 'POST',
        url: $(this).data('url') + '/removeVote',
        success: function(){
          setTimeout(() => window.location.reload(), 500);
        },
      });
    }
  });

  $(".closeVote, .recloseVote").on('click', function(){
    $.ajax({
      type: 'POST',
      url: $(this).data('id') + '/closeVote',
      success: function(){ setTimeout(() => window.location.reload(), 500); },
    });
  });

  $(".openPublicVote").on('click', function(){
    $.ajax({
      type: 'POST',
      url: $(this).data('id') + '/openPublicVote',
      success: function(){ setTimeout(() => window.location.reload(), 500); },
    });
  });

  $(".openOtherPublicVote").on('click', function(){
    let titolVotacio = prompt($(this).data('title'), "");
    if (titolVotacio && confirm('T\u00edtol: ' + titolVotacio + '\n\nEst\xE0s segur que vols obrir aquesta esmena?')) {
      $.ajax({
        type: 'POST',
        data: { 'title': titolVotacio },
        url: $(this).data('id') + '/openOtherPublicVote',
        success: function(){ setTimeout(() => window.location.reload(), 500); },
      });
    }
  });

  $(".refreshVote").on('click', function(){
    const uid = $(this).data('uid');
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