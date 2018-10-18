$( document ).ready(function() {
    $( "form" ).submit(function( event ) {
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
            return;
        }

        // prevent submission
        event.preventDefault();
    });
});

