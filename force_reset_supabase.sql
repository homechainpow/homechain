-- 🚨 HomeChain Force Reset SQL 🚨
-- Run this in your Supabase SQL Editor (https://supabase.com/dashboard/project/qmlcekoypbutzsliqqkm/sql)

-- 1. Wipe all data from the active tables
TRUNCATE TABLE blocks, transactions, rewards, holders CASCADE;

-- 2. Reset stats to zero
DELETE FROM stats;
INSERT INTO stats (id, height, total_supply, total_txs) VALUES (1, 0, 0, 0);

-- 3. Verify triggers are correctly set (Optional but recommended)
CREATE OR REPLACE FUNCTION update_holder_balance_tx()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.sender != 'SYSTEM' THEN
        INSERT INTO holders (address, balance)
        VALUES (NEW.sender, -NEW.amount)
        ON CONFLICT (address) DO UPDATE
        SET balance = holders.balance - EXCLUDED.balance,
            last_updated = NOW();
    END IF;
    INSERT INTO holders (address, balance)
    VALUES (NEW.receiver, NEW.amount)
    ON CONFLICT (address) DO UPDATE
    SET balance = holders.balance + EXCLUDED.balance,
        last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_holder_balance_rew()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO holders (address, balance)
    VALUES (NEW.receiver, NEW.amount)
    ON CONFLICT (address) DO UPDATE
    SET balance = holders.balance + EXCLUDED.balance,
        last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_update_bal_tx ON transactions;
CREATE TRIGGER tr_update_bal_tx AFTER INSERT ON transactions FOR EACH ROW EXECUTE FUNCTION update_holder_balance_tx();

DROP TRIGGER IF EXISTS tr_update_bal_rew ON rewards;
CREATE TRIGGER tr_update_bal_rew AFTER INSERT ON rewards FOR EACH ROW EXECUTE FUNCTION update_holder_balance_rew();

-- 4. Final check
SELECT 'Database Reset Successful' as Status;
