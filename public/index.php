<?php

// This path is relative to this application's public/ directory.
$APP_ROOT =
    isset($_SERVER['YODA_APP_ROOT'])
        ? $_SERVER['YODA_APP_ROOT']
        : '../../extuser';

if (chdir($APP_ROOT) === FALSE) {
    // This is a configuration / deployment error that should be caught before release.
    echo(
          '<pre>'
        .   "Sorry, something went wrong on the server."
        . "\nPlease contact a yoda-portal administrator."
        . '</pre>'
    );
    error_log(
          'Configuration error in yoda-portal\'s public/index.php: '
        . 'Could not find App directory at \'' . $APP_ROOT . '\'.'
    );
    http_response_code(500);
} else {
    require('index.php');
}
