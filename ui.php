<?php

// Service user requests.

// Utility functions {{{

function get_csrf_hash() {
    return 'aoeu';
}

// }}}

if (match_path(request_path(), '/')) {
    echo '<a href="/user/activate/some_hash">/user/activate/some_hash</a>';

} elseif (match_path(request_path(), '/user/activate/:hash', $vars)) {
    #var_dump($vars);

    $u = user_find_by_hash($vars['hash']);

    if ($u === null) {
        http_response_code(404);
        echo 'Sorry, your activation link has expired.';
    } elseif ($u['password'] !== null) {
        http_response_code(404);
        echo 'Your account is already activated.';

    } else {
        // User has a valid activation URL.
        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            if (isset($_POST['username'])
             && isset($_POST['password'])
             && isset($_POST['password_again'])
             && strlen($_POST['username']) > 0
             && strlen($_POST['password']) > 0
             && strlen($_POST['password_again']) > 0
             && $_POST['password'] === $_POST['password_again']
             && $_POST['username'] === $u['username']) {

                $username     = $u['username'];
                $creator_user = $u['creator_user'];

                $pw_hash = password_hash($_POST['password'], PASSWORD_BCRYPT);

                user_update($u['username'],
                            array('password'  => $pw_hash,
                                  'hash'      => null,
                                  'hash_time' => null));

                echo 'Your password has been saved!';

                send_mail($username, "You have successfully activated your Yoda account", <<<EOF
Hello $username,

Your Yoda account has successfully been activated.
You can now user your credentials (your e-mail address and the password you
provided earlier) to login to any Yoda service.

Please contact the helpdesk by replying to this e-mail if you have any
questions.

Kind regards,

The Yoda External User Service
EOF
);

                send_mail($creator_user, "$username has activated their Yoda account", <<<EOF
Hello $creator_user,

$username, whom you've invited to Yoda, has activated their account.

Kind regards,

The Yoda External User Service
EOF
);


                //var_dump($_POST);
            } else {
                echo "FOUT"; //xxx
            }
        } else {
            render_view('activate', array('username' => $u['username']));
        }
    }

} elseif (match_path(request_path(), '/info')) {
    // XXX
    phpinfo();

} else {
    http_response_code(404);
    render_view('404');
    //echo '<a href="/">Go back</a>';
}
