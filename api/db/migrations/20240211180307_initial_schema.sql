-- migrate:up

CREATE TABLE if not exists public."user"
(
    id              uuid                    NOT NULL,
    email           character varying(320)  NOT NULL,
    hashed_password character varying(1024) NOT NULL,
    is_active       boolean                 NOT NULL,
    is_superuser    boolean                 NOT NULL,
    is_verified     boolean                 NOT NULL
);


-- migrate:down

drop table if exists public."user";
