-- migrate:up

CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- Add that line if uuid-ossp extension is not activated yet

create table public."user"
(
    id              uuid         not null DEFAULT uuid_generate_v4() primary key,
    full_name       varchar(255),
    email           varchar(255) not null,
    hashed_password varchar      not null,
    is_active       boolean      not null DEFAULT false,
    is_superuser    boolean      not null DEFAULT false
);

create unique index ix_user_email
    on public."user" (email);

ALTER TABLE public.user
    ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- set updated_at time on each UPDATE operation
CREATE OR REPLACE FUNCTION update_timestamp()
    RETURNS TRIGGER AS
$$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Creating the trigger for users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE
    ON public.user
    FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- migrate:down

drop table if exists public."user";
