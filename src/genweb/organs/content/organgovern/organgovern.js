$("#acords-tab").on("click", function(){
  $('.spinner-acords-tab').removeClass('d-none');
  $.ajax({
    type: 'GET',
    url: $(location).attr('href') + '/getAcordsOrgangovern',
    success: function(result){
      data = $.parseJSON(result);
      $.each(data, function(key, value){
        var acordHTML = '<tr>';
        acordHTML += '<td style="vertical-align: middle;">';
        acordHTML += '<i class="bi bi-check me-1" aria-hidden="True"></i>';
        acordHTML += '<a href="' + value['absolute_url'] + '">';
        acordHTML += value['title'];
        acordHTML += '</a>';
        acordHTML += '</td>';
        acordHTML += '<td class="text-center align-middle">';
        if (value['agreement']){
          acordHTML += '<span>';
          acordHTML += value['agreement'];
          acordHTML += '</span>';
        }
        acordHTML += '</td>';
        acordHTML += '<td style="min-width: 100px" class="text-center align-middle">';
        acordHTML += '<span class="estatpunt">';
        acordHTML += '<i class="bi bi-circle-fill boletaGran" aria-hidden="true" style="color: ' + value['color'] + ';"></i> ';
        acordHTML += '<span> ';
        acordHTML += value['estatsLlista'];
        acordHTML += '</span>';
        acordHTML += '</span>';
        acordHTML += '</td>';
        acordHTML += '</tr>';
        $("#acordsTbody").append(acordHTML)
      });
      $('.spinner-acords-tab').addClass('d-none');
    },
  })
  $("#acords-tab").unbind("click");
});

$("#actes-tab").on("click", function(){
  $('.spinner-actas-tab').removeClass('d-none');
  $.ajax({
    type: 'GET',
    url: $(location).attr('href') + '/getActesOrgangovern',
    success: function(result){
      data = $.parseJSON(result);
      $.each(data, function(key, value){
        var actaHTML = '<tr>';
        actaHTML += '<td>';
        actaHTML += '<i class="bi bi-file-text me-1" aria-hidden="true"></i>';
        actaHTML += '<a href="' + value['absolute_url'] + '">';
        actaHTML += value['title'];
        actaHTML += '</a>';
        actaHTML += '</td>';
        actaHTML += '<td class="text-center">';
        if (value['data']){
          actaHTML += '<span>';
          actaHTML += value['data'];
          actaHTML += '</span>';
        }
        actaHTML += '</td>';
        actaHTML += '</tr>';

        $("#actesTbody").append(actaHTML)
      });
      $('.spinner-actas-tab').addClass('d-none');
    },
  })
  $("#actes-tab").unbind("click");
});