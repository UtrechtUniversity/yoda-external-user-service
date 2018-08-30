<?php

// Service API requests.

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit(0);
}

// Utility functions {{{

/// Check whether the correct API secret was provided.
function is_api_request_authenticated() {
    return (isset($_SERVER['HTTP_X_YODA_EXTERNAL_USER_SECRET'])
            &&    $_SERVER['HTTP_X_YODA_EXTERNAL_USER_SECRET'] === config('api_secret'));
}

/// Decode a JSON request body, and check for required fields.
/// Returns the required fields in an assoc array.
function decode_api_request_body($fields = array()) {
    //var_dump($_SERVER);

    //$body = file_get_contents('php://input');
    //var_dump(json_decode($body));
    $data = json_decode(file_get_contents('php://input'));
    if (!is_object($data)) {
        http_response_code(400); exit(0);
    }

    $result = array();

    foreach ($fields as $f) {
        if (property_exists($data, $f)) {
            $result[$f] = $data->$f;
        } else {
            http_response_code(400); exit(0);
        }
    }

    return $result;
}

// }}}

function api_user_add($username, $creator_user, $creator_zone) {

    header('Content-Type: application/json');

    //var_dump($data);
    //var_dump($u);
    $u = user_find_by_username($username);

    if ($u !== null) {
        // If the user already exists, this is not an error.
        // It simply means we have nothing to do :-)

        echo json_encode(array('status'  => 'ok',
                               'message' => 'User already exists.'));
        http_response_code(200);
        exit(0);
    }

    $hash = random_hash(32); // 64 nibbles.

    user_create(array('username'     => $username,
                      'creator_user' => $creator_user,
                      'creator_zone' => $creator_zone,
                      'hash'         => $hash,
                      'hash_time'    => date("Y-m-d H:i:s", time())));

    $hash_url = base_url("/user/activate/$hash", true);

    // XXX
    send_mail($username, 'Welcome to Yoda!', <<<EOF
Hello $username,

A Yoda account has been created for you by $creator_user.

You can activate your account by visiting the following webpage:

$hash_url

This link will remain valid for 5 days.
Please contact the helpdesk by replying to this e-mail if you have any
questions.

Kind regards,

The Yoda External User Service
EOF
);

    send_mail($creator_user, "You have invited $username to Yoda", <<<EOF
Hello $creator_user,

On your request, $username has been invited to Yoda.
You will receive a confirmation e-mail once they have activated their account.

Please contact the helpdesk by replying to this e-mail if you have any
questions.

Kind regards,

The Yoda External User Service
EOF
);

    echo json_encode(array('status'  => 'ok',
                           'message' => 'User created.'));

    http_response_code(201); exit(0); // "Created"
}

function api_user_check_auth() {

    $authed = false;

    if (isset($_SERVER['PHP_AUTH_USER'])) {
        $name = $_SERVER['PHP_AUTH_USER'];
        $pass = $_SERVER['PHP_AUTH_PW'];

        $u = user_find_by_username($name);
        if ($u !== null && password_verify($pass, $u['password']))
            $authed = true;
    }

    //error_log("<$name:$pass>");

    if ($authed) {
        header('Content-Type: text/plain');
        echo 'Authenticated';
    } else {
        header('WWW-Authenticate: Basic realm="' + config('api_auth_check_realm') + '"');
        http_response_code(401);
    }
}



if (!is_api_request_authenticated()) {
    http_response_code(403); exit(0);

} elseif ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    // For now, only accept POST requests with JSON request body on our API.
    http_response_code(405); exit(0);
} /*elseif ($_SERVER['CONTENT_TYPE'] !== 'application/json') {
    // For now, only accept JSON request bodies.
    http_response_code(415); exit(0); // "Unsupported Media Type"
    }*/

if (match_path(request_path(), '/api/user/add')) {
    $data = decode_api_request_body(array('username',
                                          'creator_user',
                                          'creator_zone'));

    api_user_add($data['username'],
                 $data['creator_user'],
                 $data['creator_zone']);

} elseif (match_path(request_path(), '/api/user/auth-check')) {

    api_user_check_auth();

} else {
    http_response_code(404); exit(0);
}
