-- migrate:up
ALTER TABLE "user"
    ADD COLUMN status VARCHAR(10) NOT NULL DEFAULT 'pending',
    ADD COLUMN role   VARCHAR(10) NOT NULL DEFAULT 'user',
    ADD CONSTRAINT status_check CHECK (status IN ('active', 'inactive', 'pending')),
    ADD CONSTRAINT role_check CHECK (role IN ('admin', 'user'));

-- Add indexes for new columns
CREATE INDEX idx_user_status ON "user" (status);
CREATE INDEX idx_user_role ON "user" (role);

-- Migrate existing data
UPDATE "user"
SET status = CASE
                 WHEN is_active = TRUE THEN 'active'
                 ELSE 'inactive'
    END;

UPDATE "user"
SET role = CASE
               WHEN is_superuser = TRUE THEN 'admin'
               ELSE 'user'
    END;

-- Drop old columns
ALTER TABLE "user"
    DROP COLUMN is_active,
    DROP COLUMN is_superuser;

-- migrate:down

ALTER TABLE "user"
    ADD COLUMN is_active    BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN is_superuser BOOLEAN NOT NULL DEFAULT FALSE;

-- Revert the data changes
UPDATE "user"
SET is_active = (status = 'active');
UPDATE "user"
SET is_superuser = (role = 'admin');

-- Remove the new columns, constraints, and indexes
ALTER TABLE "user"
    DROP COLUMN status,
    DROP COLUMN role,
    DROP CONSTRAINT status_check,
    DROP CONSTRAINT role_check;

DROP INDEX idx_user_status;
DROP INDEX idx_user_role;
