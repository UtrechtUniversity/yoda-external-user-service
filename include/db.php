<?php

/// Lazily get a database connection.
function db() {

    static $pdo_ = null;

    if ($pdo_ === null) {
        // No connection yet, set it up.
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

// Database query helpers {{{

/// Quote field names (they should not contain special chars anyway).
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

// }}}
// Database query functions {{{

/// Select a record in the specified table.
/// Returns null if no record was found.
/// $pkname can be any UNIQUE column name.
function db_find($table, $pkname, $pkvalue) {
    $q = 'select * from "' . $table . '"'
         . ' where ' . dbq_quote_field($pkname)
         . ' = ?';

    $sth = db()->prepare($q);
    $sth->execute(array($pkvalue));

    $row = $sth->fetch(PDO::FETCH_ASSOC);
    if ($row === false)
        return null;
    else
        return $row;
}

/// Select a record in the specified table.
/// Returns null if no record was found.
/// $pkname can be any UNIQUE column name.
function db_find2($table, $pkname, $pkvalue, $pkname2, $pkvalue2) {
    $q = 'select * from "' . $table . '"'
         . ' where ' . dbq_quote_field($pkname)
         . ' = ? and ' . dbq_quote_field($pkname2)
         . ' = ?';

    $sth = db()->prepare($q);
    $sth->execute(array($pkvalue, $pkvalue2));

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

    db()->prepare($q)->execute($values);
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

    db()->prepare($q)->execute($values);
}

// Delete from table
// $deleteWhat = array('user_id'=> 299,
//  user_zone=>'Bla'
// )
function db_delete($table, $deleteWhatKV) {
// examples
    // delete from users where id=bla
    // delete from user_zone where user_id=1 and user_zone = 'tempZone'

    $sqlWhere = '';
    $values = array();
    foreach ($deleteWhatKV as $col => $value) {
        $values[] = $value;
        $sqlWhere .= ($sqlWhere ? ' AND ' :  ' WHERE ') .  dbq_quote_field($col) . ' = ?';
    }

    $q = 'delete from ' . $table . $sqlWhere;

    db()->prepare($q)->execute($values);
}

// Count entries in table given where clause
function db_count($table, $countWhatKV) {
    // examples
    // count(*) from user_zone where user_id = 1
    $sqlWhere = '';
    $values = array();
    foreach ($countWhatKV as $col => $value) {
        $values[] = $value;
        $sqlWhere .= ($sqlWhere ? ' AND ' :  ' WHERE ') . dbq_quote_field($col) . ' = ?';
    }

    $q = 'select count(*) as total from ' . $table . $sqlWhere;

    $sth = db()->prepare($q);
    $sth->execute($values);

    $row = $sth->fetch(PDO::FETCH_ASSOC);

    if ($row === false) {
        return null;
    }
    else {
        return $row['total'];
    }
}

