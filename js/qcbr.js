$(document).ready(function() {
    $('#share a').click(function(e) {
        e.preventDefault();
        window.open( $(this).attr('href'), '_blank', 'location=yes,width=700,height=400' );
    });
});