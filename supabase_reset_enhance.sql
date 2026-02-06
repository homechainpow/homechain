-- HomeChain SUPABASE RESET & ENHANCE
-- Run this in Supabase SQL Editor to fix synchronization issues.

-- 1. [CAUTION] Wipe existing data to start fresh sync
TRUNCATE TABLE blocks, transactions, rewards, holders CASCADE;
UPDATE stats SET height = 0, total_supply = 0, total_txs = 0 WHERE id = 1;
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM stats WHERE id = 1) THEN
        INSERT INTO stats (id, height) VALUES (1, 0);
    END IF;
END $$;

-- 2. Setup Balance Automation (Triggers)
CREATE OR REPLACE FUNCTION update_holder_balance_tx()
RETURNS TRIGGER AS $$
BEGIN
    -- Update Sender (- amount)
    IF NEW.sender != 'SYSTEM' THEN
        INSERT INTO holders (address, balance)
        VALUES (NEW.sender, -NEW.amount)
        ON CONFLICT (address) DO UPDATE
        SET balance = holders.balance - EXCLUDED.balance,
            last_updated = NOW();
    END IF;

    -- Update Receiver (+ amount)
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

-- 3. Enable Realtime
ALTER PUBLICATION supabase_realtime ADD TABLE blocks, transactions, rewards, stats;
