// Pattern for password validation
var patt = /^(?=.*?[A-Z])(?=(.*[a-z]){1,})(?=(.*[\d]){1,})(?=(.*[\W]){1,})(?!.*\s).{10,32}$/

$(document).ready(function() {
    // Warn user if capitals are used in username.
    $('#f-forgot-password-username').on('input',function(e){
        if($('#f-forgot-password-username').val().replace(/[^A-Z]/g, "").length > 0) {
            $('#capitals').removeClass("hidden");
        } else {
            $('#capitals').addClass("hidden");
        }
    });

    // solely disable submit button intially for password validation
    $('form[validationProcess="YodaPasswordValidation"] input[type="submit"]').prop('disabled', true);

    $('form').submit(function(event) {
        // handles password/password again validation in forms for
        // 1) activation
        // 2) password reset
        if ($(this).attr('validationProcess')=='YodaPasswordValidation') {
            password        =  $('input[name="password"]').val();
            passwordAgain   =  $('input[name="password_again"]').val();

            if (password.length==0) {
                passwordAlert('Please fill in a password', false);
            }
            else if (password != passwordAgain) {
                passwordAlert('The entered passwords are not the same.', false);
            }
            else if(!patt.test(password)){
                passwordAlert('The passwords given do not meet the requirements as stated below.', false);
            }
            else {
                $("input[type='submit']").prop('disabled', true);
                return;
            }
            // prevent submission
            event.preventDefault();
        } else {
            $("input[type='submit']").prop('disabled', true);
        }
    });

    $('#f-activation-submit').click(function(){
        if (!$('#cb-activation-tou').prop('checked')) {
           alertBox('Please accept the terms of use.');
           return false;
        }
    });

    // password checking specific
    $('input[name="password"]').keyup(checkPassword);
    $('input[name="password_again"]').keyup(checkPasswordMatch);

});

// live validation
function checkPassword()
{
    password        =  $('input[name="password"]').val();
    passwordAgain   =  $('input[name="password_again"]').val();

    if (password.length==0) {
        passwordAlert('Please fill in a password', false);
    }
    else if(!patt.test(password)){
        passwordAlert('Password given does not meet the requirements as stated below.', false);
    }
    else {
        if (passwordAgain.length==0) {
            passwordAlert('Please confirm your password', false);
        }
        else {
            if (passwordAgain!=password) {
                passwordAlert('Confirmation password is not equal', false);
            }
            else {
                passwordAlert('Passwords are equal and conform requirements', true);
            }
        }
    }
}

// hier alleen checken of ze overeenkomen?? of voor edits van beide, allebei de velden testen?
function checkPasswordMatch()
{
    password        =  $('input[name="password"]').val();
    passwordAgain   =  $('input[name="password_again"]').val();

    if (password.length==0) {
        passwordAlert('Please fill in a password', false);
    }
    else if (passwordAgain.length==0) {
       passwordAlert('Please confirm your password', false);
    }
    else if (password != passwordAgain) {
        passwordAlert('The confirmation passwords is not the same.', false);
    }
    else {
        if(!patt.test(password)) {
            passwordAlert('Password is not conform requirements', false);
        }
        else {
            passwordAlert('Passwords are equal and conform requirements', true);
        }
    }
}

function passwordAlert(alert, submitState) {
    alertBox(alert);
    $("input[type='submit']").prop('disabled', !submitState);
}

function alertBox(alert) {
    $('.alert-warning').fadeOut(30, function () {
        $(this).html(alert);
    }).fadeIn(30);
}