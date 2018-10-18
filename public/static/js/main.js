$(document).ready(function() {
    // Warn user if capitals are used in username.
    $('#f-forgot-password-username').on('input',function(e){
        if($('#f-forgot-password-username').val().replace(/[^A-Z]/g, "").length > 0) {
            $('#capitals').removeClass("hidden");
        } else {
            $('#capitals').addClass("hidden");
        }
    });

    $('form').submit(function(event) {
        // handles password/password again validation in forms for
        // 1) activation
        // 2) password reset
        if ($(this).attr('validationProcess')=='YodaPasswordValidation') {
            var patt = /^(?=.*?[A-Z])(?=.*?[0-9)(?=.*?[a-z])(?=.*?[!@#=?<>()\/\&]).{10,32}$/;

            password        =  $('input[name="password"]').val();
            passwordAgain   =  $('input[name="password_again"]').val();

            if (password.length==0) {
                $('.alert-warning').removeClass('hide').html('Please fill in a password');
            }
            else if (password != passwordAgain) {
                $('.alert-warning').removeClass('hide').html('The entered passwords are not the same.');
            }
            else if(!patt.test(password)){
                $('.alert-warning').removeClass('hide').html('The passwords given do not meet the requirements as stated below.');
            }
            else {
                $(this).find("input[type='submit']").prop('disabled', true);
                return;
            }
            // prevent submission
            event.preventDefault();
        } else {
            $(this).find("input[type='submit']").prop('disabled', true);
        }
    });

// Activation handling specifics
    $('#f-activation-submit').prop('disabled', true);

    $('#cb-activation-tou').click(function(){
        $('#f-activation-submit').prop('disabled',!$(this).prop('checked'));
    });
});
