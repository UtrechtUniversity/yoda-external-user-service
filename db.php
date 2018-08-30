<?php

/// Lazily get a database connection.
function db() {

    static $pdo_ = null;

    if ($pdo_ === null) {
        try {
            $pdo_ = new \PDO(sprintf("pgsql:host=%s;port=%d;dbname=%s;user=%s;password=%s",
                                     config('db_host'),
                                     config('db_port'),
                                     config('db_name'),
                                     config('db_user'),
                                     config('db_password')));
        } catch (PDOException $e) {
            // Avoid logging the connect string.
            throw (new Exception('Could not connect to user database'));
        }

        $pdo_->setAttribute(\PDO::ATTR_ERRMODE, \PDO::ERRMODE_EXCEPTION);
    }
    return $pdo_;
}
