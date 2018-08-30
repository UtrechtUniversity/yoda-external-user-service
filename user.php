<?php

function user_find_by_username($username) {
    return db_find(config('db_user_table'), 'username', $username);
}

function user_find_by_hash($hash) {
    return db_find(config('db_user_table'), 'hash', $hash);
}

function user_create($kvs) {
    //db_insert(config('db_user_table'),
    //          array('username'     => $user['username'],
    //                'creator_user' => $user['creator_user'],
    //                'creator_zone' => $user['creator_zone']));
    db_insert(config('db_user_table'), $kvs);
}


function user_update($username, $kvs) {
    db_update(config('db_user_table'),
              'username', $username,
              $kvs);
}

//function user_create($username, $creator_user, $creator_zone) {
//
//}

/*
class User {
    $username;
    $password;
    $hash;
    $creator_user;
    $creator_zone;

    function find_by_username($username) {
        return db_find(config('db_user_table'), 'username', $username);
    }
    function find_by_hash($hash) {
    }
    function update() { }

    create($
}
 */
