<?php
require_once('common.php');

// Service user requests.

function isValidPassword($password)
{
    // - It must be between 10 and 32 characters in length
    // - It must not contain diacritics such as é, ö, and ç
    // - It must comply with at least 3 of the following rules:
    //   - At least 1 capital letter A-Z
    //   - At least 1 lowercase letter a-z
    //   - At least 1 number 0-9
    //   - At least 1 special character, such as: !@#$%&*()=?_ 

    // Match the printable ASCII range (' ' to '~'), excludes control
    // characters and unicode characters outside of ASCII.
    $basePattern = '/^[\x20-\x7e]{10,32}$/';

    // [:print:] is avoided ^ since it may match non-ASCII characters, which
    // are not allowed according to UU policy.

    // 3 of 4 of these requirements must match
    $subPattern = array();
    $subPattern[] = '/[A-Z]/';
    $subPattern[] = '/[a-z]/';
    $subPattern[] = '/[0-9]/';
    $subPattern[] = '/[^A-Za-z0-9]/';

    $validTypeCounter = 0; //

    if (preg_match($basePattern, $password) !== 1) {
        return false;
    }

    foreach($subPattern as $pattern) {
        if (preg_match($pattern, $password) === 1) {
            $validTypeCounter++;
        }
    }

    if ($validTypeCounter >= 3) {
        return true;
    }
    return false;
}


if (match_path(request_path(), '/user/activate/:hash', $vars)) {

    $u = user_find_by_hash($vars['hash']);

    if ($u === null || $u['password'] !== null) {
        // There is no user with this activation hash.
        // It may have already been used, or it may be simply invalid
        http_response_code(404);

        render_view('activation-hash-expired');

    } else {
        // User has a valid activation URL.
        $username     = $u['username'];
        $creator_user = $u['creator_user'];

        if ($_SERVER['REQUEST_METHOD'] === 'POST'
         && isset($_POST['username'])
         && isset($_POST['password'])
         && isset($_POST['password_again'])
         && $_POST['username'] === $username) {

            // Any POST request for which the above checks fail has been
            // tampered with and does not need special error reporting.
            $err = null;

            // Are all fields filled in?
            if (strlen($_POST['username']) === 0
                || strlen($_POST['password']) === 0
                || strlen($_POST['password_again']) === 0
            ) {

                $err = 'Please fill in all required fields.';

                // Do the passwords match?
            } elseif ($_POST['password'] !== $_POST['password_again']) {
                $err = 'Please re-enter your password, the two provided passwords did not match.';
            } elseif(!isValidPassword($_POST['password'])) {
                $err = 'Your password is not in accordance with requirements as stated below. Please choose a different password.';
            }


            if ($err !== null) {
                // Input invalid. Report the problem to the user and allow re-entry.
                render_view('activate', array('username' => $u['username'],
                                              'error'    => $err));
                http_response_code(200);
                exit(0);
            }

            $pw_hash = password_hash($_POST['password'], PASSWORD_BCRYPT);

            user_update($username,
                        array('password'  => $pw_hash,
                              'hash'      => null,
                              'hash_time' => null));

            send_mail_template($username, config('mail_activation-succesful_subject'),
                               'activation-succesful',
                               array('USERNAME' => $username));

            send_mail_template($creator_user, config('mail_invitation-accepted_subject'),
                               'invitation-accepted',
                               array('USERNAME' => $username,
                                     'CREATOR'  => $creator_user));

            render_view('activation-succesful', array('username' => $u['username']));

        } else {
            // GET request, allow the user to fill in a password.
            render_view('activate', array('username' => $u['username']));
        }
    }
} else if (request_path() == '/user/forgot-password') {
    if ($_SERVER['REQUEST_METHOD'] === 'POST'
        && isset($_POST['username'])) {

        $err = null;

        // Are all fields filled in?
        if (strlen($_POST['username']) === 0) {
            $err = 'Please fill in all required fields.';
        } else {
            // Username exists?
            $u = user_find_by_username($_POST['username']);

            if (is_null($u)) {
                $err = 'Only external users can reset their password.';
            }
        }

        if ($err !== null) {
            // Input invalid. Report the problem to the user and allow re-entry.
            render_view('forgot-password', array('error' => $err));
            http_response_code(200);
            exit(0);
        }

        // Generate a hash and update the hash in the database.
        $hash = random_hash(32); // 64 nibbles / characters.
        $hash_url = base_url("/user/reset-password/$hash", true);

        user_update($u['username'],
            array('hash'  => $hash,
                'hash_time' => date("Y-m-d H:i:s", time())));

        // Send an reset password e-mail.
        send_mail_template($u['username'], config('mail_reset_password_subject'),
            'reset-password',
            array('USERNAME' => $u['username'],
                'HASH_URL' => $hash_url));

        render_view('forgot-password-succesful', array('username' => $u['username']));

    } else {
        // GET request, show form.
        render_view('forgot-password');
    }
} else if (match_path(request_path(), '/user/reset-password/:hash', $vars)) {

    $u = user_find_by_hash($vars['hash']);

    if ($u === null) {
        // There is no user with this hash.
        http_response_code(404);
        render_view('404');
    } else {
        // User has a valid reset password URL.
        $username = $u['username'];

        if ($_SERVER['REQUEST_METHOD'] === 'POST'
            && isset($_POST['username'])
            && isset($_POST['password'])
            && isset($_POST['password_again'])
            && $_POST['username'] === $username) {

            $err = null;

            // Are all fields filled in?
            if (strlen($_POST['username']) === 0
                || strlen($_POST['password']) === 0
                || strlen($_POST['password_again']) === 0) {

                $err = 'Please fill in all required fields.';

                // Do the passwords match?
            } elseif($_POST['password'] !== $_POST['password_again']) {
                $err = 'Please re-enter your password, the two provided passwords did not match.';

            } elseif(!isValidPassword($_POST['password'])) {
                $err = 'Your password is not in accordance with requirements as stated below. Please choose a different password.';
            }

            if ($err !== null) {
                // Input invalid. Report the problem to the user and allow re-entry.
                render_view('reset-password', array('username' => $username,
                    'error'    => $err));
                http_response_code(200);
                exit(0);
            }

            $pw_hash = password_hash($_POST['password'], PASSWORD_BCRYPT);

            user_update($username,
                array('password'  => $pw_hash,
                    'hash'      => null,
                    'hash_time' => null));

            render_view('reset-password-succesful', array('username' => $username));

        } else {
            // GET request, allow the user to fill in a password.
            render_view('reset-password', array('username' => $u['username']));
        }
    }

} else {
    // Non-existent UI page.
    // Note: We have no '/' route.
    http_response_code(404);
    render_view('404');
}

