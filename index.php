<?php

include_once('common.php');

$path = $_SERVER['PATH_INFO'];

if (strpos($path, '/api') === 0) {
    // Service API requests.

    if (!is_api_request_authenticated()) {
        http_response_code(400); exit(0);

    } elseif ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        // For now, only accept POST requests with JSON request body on our API.
        http_response_code(405); exit(0);
    } elseif ($_SERVER['CONTENT_TYPE'] !== 'application/json') {
        // For now, only accept JSON request bodies.
        http_response_code(415); exit(0); // "Unsupported Media Type"
    }

    if (match_url($path, '/api/user/add')) {
        $data = decode_api_request_body(array('username',
                                              'creator',
                                              'creator_zone'));
        var_dump($data);
        echo "OK!\n";

    } else {
        http_response_code(404); exit(0);
    }


} else {
    // Service user requests.

    if (match_url($path, '/')) {
        echo '<a href="/user/activate/some_hash">/user/activate/some_hash</a>';

    } elseif (match_url($path, '/user/activate/:hash', $vars)) {
        #var_dump($vars);
        render_view('activate');

    } elseif (match_url($path, '/info')) {
        phpinfo();

    } else {
        http_response_code(404);
        echo '<a href="/">Go back</a>';
    }
}
