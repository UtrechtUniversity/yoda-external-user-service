<?php

$config_ = array();

function config($key, $val = null) {
    global $config_;
    if (isset($val)) {
        $config_[$key] = $val;
    }
    return $config_[$key];
}

config('db_host',     'localhost');
config('db_port',     5432);
config('db_name',     'extuser');
config('db_user',     '');
config('db_password', '');

config('api_secret',  '');

if (file_exists('config_local.php'))
    include('config_local.php');
