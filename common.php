<?php

session_start();

include_once('config.php');
include_once('db.php');

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

function base_url($path='') {
    return $path;
}

function get_csrf_hash() {
    return 'aoeu';
}

function escape_html($str) {
    return htmlentities($str, ENT_HTML5, 'UTF-8');
}

function render_view($name, $data=array()) {
    if (!isset($data['title'])) { $data['title'] = 'Yoda external user service'; }

    #var_dump($data);

    include('views/common/start.phtml');
    include("views/$name.phtml");
    include('views/common/end.phtml');
}

$routes_ = array();

function match_url($path, $pattern, &$matches = array()) {
    $pattern = preg_replace('/\\\:([a-zA-Z][a-zA-Z0-9]*)/', '(?P<$1>[^\/]+)',
                            preg_quote($pattern, '/'));
    #echo "==$pattern==$path==\n";
    return preg_match("/^$pattern\$/", $path, $matches);
}
