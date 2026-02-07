-- Add difficulty column to blocks table for better analytics
ALTER TABLE blocks ADD COLUMN IF NOT EXISTS difficulty TEXT;

-- Optionally backfill from target column (they're the same for now)
UPDATE blocks SET difficulty = target WHERE difficulty IS NULL;
