$(document).ready(function() {

    $('.confirmRedirect').click(function() {
        var redirect = $(this).attr('data-redirect');
        if (confirm('Est\xE0s segur que vols canviar la visibilitat del fitxer? Aquesta acci\xF3 pot reempla\xE7ar el fitxer actual.')) {
            window.location.href = redirect;
        }
    });
});