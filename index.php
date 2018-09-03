<?php

// Application entrypoint.

require_once('common.php');

// The application consists of an API and a user interface.
// Load the correct component by looking at the URL.

if (strpos(request_path(), '/api') === 0) {

    // Service API requests.
    require('routes-api.php');

} else {

    // Service user requests.
    require('routes-ui.php');
}
