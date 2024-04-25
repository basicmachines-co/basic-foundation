-- migrate:up

alter table "user"
    add column if not exists first_name varchar;
alter table "user"
    add column if not exists last_name varchar;

-- migrate:down

alter table "user"
    drop column first_name;
alter table "user"
    drop column last_name;
