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

/// Assumes field names do not contain odd characters.
function dbq_quote_field($name) {
    return "\"$name\"";
}

/// Construct a list of field names.
function dbq_field_list($fields) {
    return ' (' . join(', ', array_map('dbq_quote_field', $fields)) . ')';
}

/// Construct a list of value placeholders.
function dbq_value_placeholder_list($fields) {
    //return ' (' . join(', ', array_map(function($s){return ":$s";}, $fields)) . ')';
    return ' (' . join(', ', array_map(function($s){return '?';}, $fields)) . ')';
}

/// Select a record in the specified table.
function db_find($table, $pkname, $pkvalue) {
    $q = 'select * from "' . $table . '"'
         . ' where ' . dbq_quote_field($pkname)
         . ' = ?';

    //echo $q;
    $sth = db()->prepare($q);
    $sth->execute(array($pkvalue));
    //$sth->execute(array('piet.throwaway@v1a.nl'));
    //$sth->debugDumpParams();
    $row = $sth->fetch(PDO::FETCH_ASSOC);
    if ($row === false)
        return null;
    else
        return $row;
}

/// Insert a record in the specified table.
function db_insert($table, $kvs) {
    $fields = array_keys($kvs);
    $values = array_values($kvs);

    $q = 'insert into "' . $table . '"'
         . dbq_field_list($fields)
         . ' values '
         . dbq_value_placeholder_list($fields);

    //echo $q;
    db()->prepare($q)->execute($values);
    //db()->prepare($q)->execute($kvs);
}

/// Update a record in the specified table.
function db_update($table, $pkname, $pkvalue, $kvs) {
    $fields = array_keys($kvs);
    $values = array_values($kvs);

    $q = 'update "' . $table . '" set '
         . dbq_field_list($fields)
         . ' = '
         . dbq_value_placeholder_list($fields)
         . ' where ' . dbq_quote_field($pkname)
         . ' = ?';

    $values[] = $pkvalue;

    //echo $q;
    db()->prepare($q)->execute($values);
}

