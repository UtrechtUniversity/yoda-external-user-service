<?php

require_once('common.php');

if (strpos(request_path(), '/api') === 0) {
    // Service API requests.

    include('api.php');

} else {
    // Service user requests.

    include('ui.php');
}
