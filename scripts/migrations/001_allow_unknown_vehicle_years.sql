BEGIN;

ALTER TABLE vehicle_model
    ALTER COLUMN year_from DROP NOT NULL;

ALTER TABLE vehicle_model
    DROP CONSTRAINT IF EXISTS ck_vehicle_model_year_range;

ALTER TABLE vehicle_model
    ADD CONSTRAINT ck_vehicle_model_year_range
    CHECK (year_from IS NULL OR year_to IS NULL OR year_to >= year_from);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'uk_vehicle_model'
          AND conrelid = 'vehicle_model'::regclass
    ) THEN
        ALTER TABLE vehicle_model
            ADD CONSTRAINT uk_vehicle_model
            UNIQUE NULLS NOT DISTINCT (make, model, year_from, year_to);
    END IF;
END $$;

COMMIT;
