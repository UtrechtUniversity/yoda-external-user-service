<?php

// External user service configuration.
// This file contains the default settings; It should not be modified.
// A config_local.php file must be created to fill in DB/API/SMTP credentials,
// and to add any desired customizations.

function config($key, $val = null) {
    static $config_ = array();

    if (isset($val))
        $config_[$key] = $val;
    return $config_[$key];
}

// Database connection info.
config('db_host',       'localhost');
config('db_port',       5432);
config('db_name',       'extuser');
config('db_user',       '');
config('db_password',   '');

// Table that holds all external user info.
config('db_user_table', 'users');

// The API secret that must be provided by all clients that make use of the
// external user API.
config('api_secret',    '');

// The HTTP Basic auth realm that will be indicated at the auth-check API route.
config('api_auth_check_realm', 'yoda-extuser');

// Mail server details.
config('smtp_host',            '');
config('smtp_port',           587);
config('smtp_user',            '');
config('smtp_password',        '');
config('smtp_security',     'tls'); // Either 'tls' or 'ssl'.
                                    // Choose 'tls' when the port is 587,
                                    // and 'ssl' when the port is 465.

// General e-mail customization.
config('smtp_from_name',       'Yoda External User Service');
config('smtp_from_address',    ''); // Restrictions may apply.
                                    // This likely needs to match the smtp_user setting.

config('smtp_replyto_name',    ''); // Redirect replies to a service/helpdesk e-mail, for example.
config('smtp_replyto_address', '');

// Mail templates and subjects.
config('mail_template',                     'example');
config('mail_invitation_subject',           'Welcome to Yoda!');
config('mail_invitation-sent_subject',      'You have invited an external user to Yoda');
config('mail_activation-succesful_subject', 'You have successfully activated your Yoda account');
config('mail_invitation-accepted_subject',  'An external user has activated their Yoda account');

if (file_exists('config_local.php'))
    require('config_local.php');
