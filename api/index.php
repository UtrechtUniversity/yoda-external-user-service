<?php

// This path is relative to this application's public/ directory.
$APP_ROOT =
    isset($_SERVER['YODA_APP_ROOT'])
        ? $_SERVER['YODA_APP_ROOT']
        : '../../yoda-external-user-service';

if (chdir($APP_ROOT) === FALSE) {
    // This is a configuration / deployment error that should be caught before release.
    echo(
          '<pre>'
        .   "Sorry, something went wrong on the server."
        . "\nPlease contact a Yoda administrator."
        . '</pre>'
    );
    error_log(
          'Configuration error in the external user service\'s api/index.php: '
        . 'Could not find App directory at \'' . $APP_ROOT . '\'.'
    );
    http_response_code(500);
} else {
    require('routes-api.php');
}
