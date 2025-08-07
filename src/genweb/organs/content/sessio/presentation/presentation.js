$(document).ready(function(){

	$('#scrollUp').on('click', function(e) {
		e.preventDefault();
		$('html, body').animate({ scrollTop: $(window).scrollTop() - 200 }, 300);
	});
	
	$('#scrollDown').on('click', function(e) {
		e.preventDefault();
		$('html, body').animate({ scrollTop: $(window).scrollTop() + 200 }, 300);
	});
});
