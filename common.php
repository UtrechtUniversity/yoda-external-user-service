<?php

session_start();

include_once('config.php');
include_once('view.php');
include_once('errors.php');
include_once('db.php');

// Utility functions {{{

function request_path() {
    return $_SERVER['PATH_INFO'];
}

function base_url($path='/') {
    return $path;
}

function match_path($path, $pattern, &$matches = array()) {
    $pattern = preg_replace('/\\\:([a-zA-Z][a-zA-Z0-9]*)/', '(?P<$1>[^\/]+)',
                            preg_quote($pattern, '/'));
    #echo "==$pattern==$path==\n";
    return preg_match("/^$pattern\$/", $path, $matches);
}

// }}}
