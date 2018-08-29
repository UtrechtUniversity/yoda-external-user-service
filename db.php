<?php

$pdo_ = new \PDO(sprintf("pgsql:host=%s;port=%d;dbname=%s;user=%s;password=%s",
                         config('db_host'),
                         config('db_port'),
                         config('db_name'),
                         config('db_user'),
                         config('db_password')));
$pdo_->setAttribute(\PDO::ATTR_ERRMODE, \PDO::ERRMODE_EXCEPTION);

$db = $pdo_;
