<?php

function config($key, $val = null) {
    static $config_ = array();

    if (isset($val))
        $config_[$key] = $val;
    return $config_[$key];
}

config('db_host',     'localhost');
config('db_port',     5432);
config('db_name',     'extuser');
config('db_user',     '');
config('db_password', '');

config('db_table',    'users');

config('api_secret',  '');

if (file_exists('config_local.php'))
    include('config_local.php');
