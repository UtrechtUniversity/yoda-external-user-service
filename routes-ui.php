<?php

// Service user requests.

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
             || strlen($_POST['password_again']) === 0) {

                $err = 'Please fill in all required fields.';

                // Do the passwords match?
            } elseif($_POST['password'] !== $_POST['password_again']) {

                $err = 'Please re-enter your password, the two provided passwords did not match.';
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
} else {
    // Non-existent UI page.
    // Note: We have no '/' route.
    http_response_code(404);
    render_view('404');
}
