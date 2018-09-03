<?php

// Service API requests.

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    // When accessing the API through a web browser, using a tool like
    // https://swagger.io, OPTIONS requests must be handled.
    // This is used to notify the web browser through CORS headers that we are
    // OK with certain sites sending requests to us.
    // See the public/.htaccess file for the relevant headers and the
    // whitelisted domains, if any.
    //
    // This OPTIONS check has no effect if the CORS headers are disabled in the
    // .htaccess file, so it can be safely included regardless.
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
/// If the required fields do not exist, sets 400 and exits.
function decode_api_request_body($fields = array()) {

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
// API route implementations {{{

/// Create a new external user.
function api_user_add($username, $creator_user, $creator_zone) {

    header('Content-Type: application/json');

    $u = user_find_by_username($username);

    if ($u !== null) {
        // If the user already exists, this is not an error.
        // It simply means we have nothing to do :-)
        //
        // This may occur if a user was added in zone A,
        // and is then added in zone B. The iRODS user is newly created, but
        // the external user already exists.

        echo json_encode(array('status'  => 'ok',
                               'message' => 'User already exists.'));
        http_response_code(200);
        exit(0);
    }

    // Generate a hash and add the user to the database.

    $hash = random_hash(32); // 64 nibbles / characters.

    user_create(array('username'     => $username,
                      'creator_user' => $creator_user,
                      'creator_zone' => $creator_zone,
                      'hash'         => $hash,
                      'hash_time'    => date("Y-m-d H:i:s", time())));

    $hash_url = base_url("/user/activate/$hash", true);

    // Send an invitation e-mail and a confirmation.

    send_mail_template($username, config('mail_invitation_subject'),
                       'invitation',
                       array('USERNAME' => $username,
                             'CREATOR'  => $creator_user,
                             'HASH_URL' => $hash_url));

    send_mail_template($creator_user, config('mail_invitation-sent_subject'),
                       'invitation-sent',
                       array('USERNAME' => $username,
                             'CREATOR'  => $creator_user));

    // Success!

    echo json_encode(array('status'  => 'ok',
                           'message' => 'User created.'));

    http_response_code(201); exit(0); // 201, "Created"
}

/// Check a user's credentials.
function api_user_check_auth() {

    $authed = false;

    // Check the credentials in the HTTP Basic auth header.

    if (isset($_SERVER['PHP_AUTH_USER'])) {
        $name = $_SERVER['PHP_AUTH_USER'];
        $pass = $_SERVER['PHP_AUTH_PW'];

        // User must exist and password hash must match.

        $u = user_find_by_username($name);
        if ($u !== null && password_verify($pass, $u['password']))
            $authed = true;
    }

    if ($authed) {
        header('Content-Type: text/plain');
        echo 'Authenticated';
    } else {
        header('WWW-Authenticate: Basic realm="' + config('api_auth_check_realm') + '"');
        http_response_code(401);
    }
}

// }}}

if (!is_api_request_authenticated()) {
    // All requests must contain an API secret.
    http_response_code(403); exit(0);

} elseif ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    // For now, only accept POST requests.
    http_response_code(405); exit(0);
}

// Perform routing.

if (match_path(request_path(), '/api/user/add')) {

    // Fetch & verify parameters from the JSON request body.
    $data = decode_api_request_body(array('username',
                                          'creator_user',
                                          'creator_zone'));

    api_user_add($data['username'],
                 $data['creator_user'],
                 $data['creator_zone']);

} elseif (match_path(request_path(), '/api/user/auth-check')) {

    // Parameters are in a Basic auth header.
    api_user_check_auth();

} else {
    // Non-existent API route.
    // No need to provide any info besides the 404 status code.
    http_response_code(404); exit(0);
}
