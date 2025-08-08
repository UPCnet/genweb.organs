$(document).ready(function(){

	$('#scrollUp').on('click', function(e) {
		e.preventDefault();
		$('html, body').animate({ scrollTop: $(window).scrollTop() - 200 }, 300);
	});
	
	$('#scrollDown').on('click', function(e) {
		e.preventDefault();
		$('html, body').animate({ scrollTop: $(window).scrollTop() + 200 }, 300);
	});

	$('#documentContentModal').on('show.bs.modal', function(event){
		var button = $(event.relatedTarget);
		var title = button.data('title');
		var content = button.data('content');
		var modal = $(this);
		modal.find('#documentContentModalLabel').html(title);
		modal.find('#documentContentModalBody').html(content);
	});

	$('#fileContentModal').on('show.bs.modal', function(event){
		var button = $(event.relatedTarget);
		var title = button.data('title');
		var url = button.data('url');
		var modal = $(this);
		modal.find('#fileContentModalLabel').html(title);

		var objectElement = modal.find('#fileContentModalObject');
        var newObject = objectElement.clone();
        newObject.attr('data', url);
        objectElement.replaceWith(newObject);
	});
});
