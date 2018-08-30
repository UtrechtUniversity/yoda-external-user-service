<?php

include_once('common.php');

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
    render_view('activate');

} elseif (match_path(request_path(), '/info')) {
    phpinfo();

} else {
    http_response_code(404);
    render_view('404');
    //echo '<a href="/">Go back</a>';
}
