<?php

session_start();

require_once('config.php');
require_once('view.php');
require_once('errors.php');
require_once('db.php');
require_once('user.php');
require_once('mail.php');
require_once('password_compat/password.php');

// Utility functions {{{

function request_path() {
    return $_SERVER['PATH_INFO'];
}

//var_dump($_SERVER);

function base_url($path='/', $absolute = false) {
    if (strlen($path) === 0 || strpos($path, '/') !== 0)
        $path = "/$path";

    if ($absolute) {
        return $_SERVER['REQUEST_SCHEME']
             . '://'
             . $_SERVER['SERVER_NAME']
             . $path;
    } else {
        return $path;
    }
}

function match_path($path, $pattern, &$matches = array()) {
    $pattern = preg_replace('/\\\:([a-zA-Z][a-zA-Z0-9]*)/', '(?P<$1>[^\/]+)',
                            preg_quote($pattern, '/'));

    return preg_match("/^$pattern\$/", $path, $matches);
}

function random_hash($length_bytes) {
    $data = openssl_random_pseudo_bytes($length_bytes, $cstrong);
    assert($cstrong === true); // Ensure "cryptographically strong" RNG.

    return bin2hex($data);
}

// }}}
