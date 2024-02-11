-- migrate:up

alter table "user"
    add column first_name varchar;
alter table "user"
    add column last_name varchar;

-- migrate:down

alter table "user"
    drop column first_name;
alter table "user"
    drop column last_name;
