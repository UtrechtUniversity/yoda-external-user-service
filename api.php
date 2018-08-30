<?php

include_once('common.php');

// Service API requests.

// Utility functions {{{

function is_api_request_authenticated() {
    return (isset($_SERVER['HTTP_X_YODA_EXTERNAL_USER_SECRET'])
            &&    $_SERVER['HTTP_X_YODA_EXTERNAL_USER_SECRET'] === config('api_secret'));
}

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

    return $data;
}

// }}}

if (!is_api_request_authenticated()) {
    http_response_code(400); exit(0);

} elseif ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    // For now, only accept POST requests with JSON request body on our API.
    http_response_code(405); exit(0);
} elseif ($_SERVER['CONTENT_TYPE'] !== 'application/json') {
    // For now, only accept JSON request bodies.
    http_response_code(415); exit(0); // "Unsupported Media Type"
}

if (match_path(request_path(), '/api/user/add')) {
    $data = decode_api_request_body(array('username',
        'creator',
        'creator_zone'));
    var_dump($data);
    echo "OK!\n";

} else {
    http_response_code(404); exit(0);
}
