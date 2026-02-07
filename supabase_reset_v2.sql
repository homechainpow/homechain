
-- Reset Supabase for V2 Chain
TRUNCATE TABLE transactions;
TRUNCATE TABLE rewards;
TRUNCATE TABLE blocks CASCADE;
UPDATE stats SET height = 0, total_supply = 0 WHERE id = 1;
