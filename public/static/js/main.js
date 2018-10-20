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
            else if(!isValidPassword(password)) {
                passwordAlert('Passwords given do not meet the requirements as stated below.', false);
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


function isValidPassword(password)   // 3 of 4 must be present. If so -> password is valid
{
    var patt = /^([a-zA-Z0-9!@#$%&*()=?]){10,32}$/

    var subpatt1 = /\d/
    var subpatt2 = /[A-Z]/
    var subpatt3 = /[a-z]/
    var subpatt4 = /[!@#$%&*()=?]/

    if (patt.test(password)) { // generic test.
        var count = 0;

        if (subpatt1.test(password)) {
            count++;
        }

        if (subpatt2.test(password)) {
            count++;
        }

        if (subpatt3.test(password)) {
            count++;
        }

        if (subpatt4.test(password)) {
             count++;
        }

        if (count>=3) {
            return true;
        }
    }
    return false;
}

function checkPassword()
{
    password        =  $('input[name="password"]').val();
    passwordAgain   =  $('input[name="password_again"]').val();

    $('.password-check-icon-ok').addClass('hide');
    $('.password-again-check-icon-ok').addClass('hide');

    if (password.length==0) {
        passwordAlert('Please fill in a password', false);
    }
    else if(!isValidPassword(password)){
        passwordAlert('Passwords given do not meet the requirements as stated below.', false);
    }
    else {
        $('.password-check-icon-ok').removeClass('hide');
        if (passwordAgain.length==0) {
            passwordAlert('Please confirm your password.', false);
        }
        else {
            if (passwordAgain!=password) {
                passwordAlert('Confirmation password is not equal.', false);
            }
            else {
                $('.password-again-check-icon-ok').removeClass('hide');
                passwordAlert('Passwords are equal and conform requirements.', true);

            }
        }
    }
}

function checkPasswordMatch()
{
    password        =  $('input[name="password"]').val();
    passwordAgain   =  $('input[name="password_again"]').val();

    $('.password-again-check-icon-ok').addClass('hide');

    if(!isValidPassword(password)) {
        passwordAlert('Passwords given do not meet the requirements as stated below.', false);
        return;
    }

    if (password.length==0) {
        passwordAlert('Please fill in a password.', false);
    }
    else if (passwordAgain.length==0) {
       passwordAlert('Please confirm your password.', false);
    }
    else if (password != passwordAgain) {
        passwordAlert('Confirmation passwords is not equal.', false);
    }
    else {
        // match is only valid if actual password is valid.
        passwordAlert('Passwords are equal and conform requirements.', true);
        $('.password-again-check-icon-ok').removeClass('hide');
    }
}

function passwordAlert(alert, submitState) {
    alertBox(alert);
    $("input[type='submit']").prop('disabled', !submitState);
}

function alertBox(alert) {
    // $('.alert-warning').fadeOut(30, function () {
    //     $(this).html(alert);
    // }).fadeIn(30);
    $('.alert-warning').html(alert);
}