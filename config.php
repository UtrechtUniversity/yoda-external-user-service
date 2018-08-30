<?php

function config($key, $val = null) {
    static $config_ = array();

    if (isset($val))
        $config_[$key] = $val;
    return $config_[$key];
}

config('db_host',       'localhost');
config('db_port',       5432);
config('db_name',       'extuser');
config('db_user',       '');
config('db_password',   '');

config('db_user_table', 'users');

config('api_secret',    '');

config('api_auth_check_realm', 'yoda-extauth');

config('smtp_host',            '');
config('smtp_port',            25);
config('smtp_user',            '');
config('smtp_password',        '');
config('smtp_from_name',       'Yoda External User Service');
config('smtp_from_address',    '');
config('smtp_replyto_name',    '');
config('smtp_replyto_address', '');

if (file_exists('config_local.php'))
    include('config_local.php');
