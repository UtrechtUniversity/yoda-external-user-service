CREATE TABLE IF NOT EXISTS "users" (
  "id" SERIAL NOT NULL PRIMARY KEY,
  "username" varchar(64) NOT NULL UNIQUE,
  "password" char(60) NULL,
  "hash" char(64) NULL UNIQUE,
  "hash_time" timestamp NULL,
  "creator_time" timestamp NOT NULL,
  "creator_user" varchar(255) NOT NULL,
  "creator_zone" varchar(255) NOT NULL
);


CREATE TABLE IF NOT EXISTS "user_zones" (
  "user_id" INTEGER NOT NULL REFERENCES users(id),
  "inviter_user" varchar(255) NOT NULL,
  "inviter_zone" varchar(255) NOT NULL,
  "inviter_time" timestamp NOT NULL,
  PRIMARY KEY (user_id, inviter_zone)
);
