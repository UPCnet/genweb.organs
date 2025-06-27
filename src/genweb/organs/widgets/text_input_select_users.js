var hideElementsSelect = function(){
  $("#form-widgets-select_users-error").removeClass("viewError");
  $("#form-widgets-select_users-warn").removeClass("viewWarn");
  $("#form-widgets-select_users-hint > tbody").html("<tr><td/><td/><td/><td/><td/></tr>");
}

var addUser = function(user){
  parent = $(user).parent().parent();
  if($("#form-widgets-signants").val().length > 0){
    $("#form-widgets-signants").val($("#form-widgets-signants").val() + ', ' + $(parent).children('.userid').html());
  }else{
    $("#form-widgets-signants").val($(parent).children('.userid').html());
  }

  $('#form-widgets-select_users-modal').modal('toggle');
}

$("#form-widgets-select_users-btn").on("click", function(){
  hideElementsSelect();
  var regexUsername = new RegExp('^[a-zA-ZñÑçÇ]{1,}\\.[a-zA-Z0-9-.ñÑçÇ]{1,}$');
  var user = $("#form-widgets-select_users-input").val();
  if(regexUsername.test(user)){
    $.ajax({
      type: 'POST',
      data: { "user" : $("#form-widgets-select_users-input").val() },
      url: 'getUsers',
      success: function(data){
        results = $.parseJSON(data);
        if(results != null && results.length > 0){
          $("#form-widgets-select_users-hint > tbody").html("");
          $.each( results, function( key, value ){
            $("#form-widgets-select_users-hint").show();
            field = "<tr class='align-middle'>";
            field += "<td class='userid'>" + value['user'] + "</td>";
            field += "<td class='fullname'>" + value['fullname'] + "</td>";
            field += "<td class='email'>" + value['email'] + "</td>";
            field += "<td class='actions'>";
            field += "<a class='btn btn-secondary' onclick='addUser(this)'>";
            field += "<i class='bi bi-plus' aria-hidden='true'></i>";
            field += "</a>";
            field += "</td>";
            field += "</tr>";
            $("#form-widgets-select_users-hint").append(field);
          });
        }else{
          $("#form-widgets-select_users-warn").addClass("viewWarn");
        }
      }
    });
  }else{
    $("#form-widgets-select_users-error").addClass("viewError");
  }
});

$("#form-widgets-select_users-btn-clear").on("click", function(){
  $("#form-widgets-signants").val("");
});