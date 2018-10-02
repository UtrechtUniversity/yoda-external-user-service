CREATE TABLE IF NOT EXISTS "users" (
  "username" varchar(255) NOT NULL PRIMARY KEY,
  "password" char(60) NULL,
  "hash" char(64) NULL UNIQUE,
  "hash_time" timestamp NULL,
  "creator_user" varchar(255) NOT NULL,
  "creator_zone" varchar(255) NOT NULL
);
