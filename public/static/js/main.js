$(document).ready(function() {
    // Warn user if capitals are used in username.
    $('#f-forgot-password-username').on('input',function(e){
        if($('#f-forgot-password-username').val().replace(/[^A-Z]/g, "").length > 0) {
            $('#capitals').removeClass("hidden");
        } else {
            $('#capitals').addClass("hidden");
        }
    });
});
