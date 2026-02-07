-- 🏙️ HomeChain V2: Production Database Setup 🏙️
-- Run this in your Supabase SQL Editor (https://supabase.com/dashboard/project/hemzvtzsyybathuprizc/sql)

-- 1. Create Core Tables
CREATE TABLE IF NOT EXISTS blocks (
    id BIGINT PRIMARY KEY,
    hash TEXT NOT NULL,
    prev_hash TEXT,
    timestamp TIMESTAMP WITH TIME ZONE,
    validator TEXT,
    tx_count INT DEFAULT 0,
    reward_count INT DEFAULT 0,
    target TEXT,
    difficulty TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    block_id BIGINT REFERENCES blocks(id) ON DELETE CASCADE,
    sender TEXT,
    receiver TEXT,
    amount BIGINT,
    data TEXT,
    timestamp TIMESTAMP WITH TIME ZONE,
    signature TEXT
);

CREATE TABLE IF NOT EXISTS rewards (
    id BIGSERIAL PRIMARY KEY,
    block_id BIGINT REFERENCES blocks(id) ON DELETE CASCADE,
    receiver TEXT,
    amount BIGINT,
    type TEXT,
    timestamp TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS stats (
    id INT PRIMARY KEY DEFAULT 1,
    height BIGINT DEFAULT 0,
    total_supply BIGINT DEFAULT 0,
    total_txs BIGINT DEFAULT 0,
    difficulty TEXT,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS holders (
    address TEXT PRIMARY KEY,
    balance BIGINT DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create Real-Time Balance Triggers
CREATE OR REPLACE FUNCTION update_holder_balance_tx()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.sender != 'SYSTEM' THEN
        INSERT INTO holders (address, balance)
        VALUES (NEW.sender, -NEW.amount)
        ON CONFLICT (address) DO UPDATE
        SET balance = holders.balance + EXCLUDED.balance,
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

-- 3. Initialize Stats
INSERT INTO stats (id, height, total_supply, total_txs) VALUES (1, 0, 0, 0) ON CONFLICT (id) DO NOTHING;

SELECT 'HomeChain V2 Database Ready' as Status;
