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
            var password      = $('input[name="password"]'      ).val();
            var passwordAgain = $('input[name="password_again"]').val();

            if (password.length == 0) {
                passwordAlert('Please fill in a password', false);
            }
            else if (password !== passwordAgain) {
                passwordAlert('The entered passwords are not the same.', false);
            }
            else if(!isValidPassword(password)) {
                passwordAlert('The password does not meet the requirements stated below.', false);
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
    $('input[name="password"]'      ).keyup(checkPasswords);
    $('input[name="password_again"]').keyup(checkPasswords);
});


function isValidPassword(password) {

    // - It must be between 10 and 32 characters in length
    // - It must not contain diacritics such as é, ö, and ç
    // - It must comply with at least 3 of the following rules:
    //   - At least 1 capital letter A-Z
    //   - At least 1 lowercase letter a-z
    //   - At least 1 number 0-9
    //   - At least 1 special character, such as: !@#$%&*()=?_ 
    //
    // First check for the right length and allowed characters.
    //
    // JS has no [:ascii:] or [:print:], so we match the printable range
    // manually (consult an ASCII table).

    if (!/^[\x20-\x7e]{10,32}$/.test(password))
        return false;

    // Password consists of only allowed characters and is of the right length.

    // At least 3 out of 4 optional patterns must match.
    var optionalPatterns = [
        /[A-Z]/,
        /[a-z]/,
        /[0-9]/,
        /[^A-Za-z0-9]/, // will match special symbols (!@#$, spaces, etc.)
    ];

    var matches = 0;

    $.each(optionalPatterns, function (i, pattern) {
        if (pattern.test(password))
            matches++;
    });

    return matches >= 3;
}

function checkPasswords() {
    var password      =  $('input[name="password"]'      ).val();
    var passwordAgain =  $('input[name="password_again"]').val();

    $('.password-check-icon-ok'      ).addClass('hide');
    $('.password-again-check-icon-ok').addClass('hide');

    // Check first password.

    if (password.length == 0) {
        passwordAlert('Please fill in a password', false);
        return;

    } else if (!isValidPassword(password)) {
        passwordAlert('The password does not meet the requirements stated below.', false);
        return;
    }

    // First password is OK. Check confirmation password.

    $('.password-check-icon-ok').removeClass('hide');

    if (passwordAgain.length == 0) {
        passwordAlert('Please confirm your password.', false);

    } else if (passwordAgain !== password) {
        passwordAlert('Confirmation password differs from original.', false);

    } else {
        $('.password-again-check-icon-ok').removeClass('hide');
        passwordAlert('Passwords are equal and satisfy the requirements.', true);
    }
}

function passwordAlert(alert, submitState) {
    alertBox(alert);
    $("input[type='submit']").prop('disabled', !submitState);
}

function alertBox(alert) {
    $('.alert-warning').html(alert);
}
