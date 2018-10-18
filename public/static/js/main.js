$(document).ready(function() {
    // Warn user if capitals are used in username.
    $('#f-forgot-password-username').on('input',function(e){
        if($('#f-forgot-password-username').val().replace(/[^A-Z]/g, "").length > 0) {
            $('#capitals').removeClass("hidden");
        } else {
            $('#capitals').addClass("hidden");
        }
    });

    // Disable form submit button after submit.
    $('form').submit(function(event) {
        if ($(this).attr('id')=='form-reset-password') { // reset form requires extra handling
            var patt = /^(?=.*?[A-Z])(?=.*?[0-9)(?=.*?[a-z])(?=.*?[!@#=?<>()\/\&]).{10,32}$/;

            if ($('#f-reset-password-password').val().length==0) {
                $('.alert-warning').removeClass('hide').html('Please fill in a password');
            }
            else if ($('#f-reset-password-password').val() != $('#f-reset-password-password-again').val()) {
                $('.alert-warning').removeClass('hide').html('The entered passwords are not the same.');
            }
            else if(!patt.test($('#f-reset-password-password').val())){
                $('.alert-warning').removeClass('hide').html('The passwords given do not meet the requirements as stated below.');
            }
            else {
                //$('.alert-warning').removeClass('hide').html('Passwords are correct.');
                // submit form!
                $(this).find("input[type='submit']").prop('disabled', true);
                return;
            }
            // prevent submission
            event.preventDefault();

        } else {
            $(this).find("input[type='submit']").prop('disabled', true);
        }
    });
});
