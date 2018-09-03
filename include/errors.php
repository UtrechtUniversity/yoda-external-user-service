<?php

// Sets global error handling and provides a 'fail' function.

$in_error_ = false;

set_error_handler(function ($errno, $errstr, $errfile, $errline, $errcontext) {
    if ($errno == E_USER_ERROR) {
        error_log("fatal error at $errfile line $errline: $errstr");

        global $in_error_; // Prevent stacked errors.
        if ($in_error_) exit(1);
        $in_error_ = true;

        http_response_code(500);
        render_view('500');
        return true;
    }
    return false;
});

set_exception_handler(function ($e) {
    error_log('unhandled exception:');
    error_log($e);

    global $in_error_; // Prevent stacked errors.
    if ($in_error_) exit(1);
    $in_error_ = true;

    http_response_code(500);
    try {
        render_view('500');
    } catch (Exception $e) { }
});

/// Throw an exception.
/// To be used for unrecoverable errors (e.g: logic errors).
function fail($msg) {
    throw new Exception($msg);
}
