<?php

// User table functions.
function user_find_by_username($username) {
    return db_find(config('db_user_table'), 'username', $username);
}

function user_find_by_hash($hash) {
    return db_find(config('db_user_table'), 'hash', $hash);
}

function user_create($kvs) {
    db_insert(config('db_user_table'), $kvs);
}

function user_update($username, $kvs) {
    db_update(config('db_user_table'),
              'username', $username,
              $kvs);
}

// User zones table functions.
function invitation_create($kvs) {
    db_insert(config('db_user_zones_table'), $kvs);
}

function invitation_find_by_id_and_zone($user_id, $inviter_zone) {
    return db_find2(config('db_user_zones_table'),
                    'users_id', $user_id,
		    'inviter_zone', $inviter_zone);
}