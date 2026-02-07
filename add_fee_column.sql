-- Add fee column to transactions table
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS fee BIGINT DEFAULT 1000000;

-- Update existing transactions to have the default fee (0.01 HOME)
UPDATE transactions SET fee = 1000000 WHERE fee IS NULL;
