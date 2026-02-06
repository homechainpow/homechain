-- HomeChain Enhanced Supabase Schema with Triggers

-- 1. Tables (Ensure they exist)
CREATE TABLE IF NOT EXISTS blocks (
    id BIGINT PRIMARY KEY,
    hash TEXT UNIQUE NOT NULL,
    prev_hash TEXT,
    timestamp TIMESTAMPTZ NOT NULL,
    validator TEXT NOT NULL,
    tx_count INT DEFAULT 0,
    reward_count INT DEFAULT 0,
    target TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    block_id BIGINT REFERENCES blocks(id) ON DELETE CASCADE,
    sender TEXT NOT NULL,
    receiver TEXT NOT NULL,
    amount BIGINT NOT NULL,
    data JSONB,
    timestamp TIMESTAMPTZ NOT NULL,
    signature TEXT
);

CREATE TABLE IF NOT EXISTS rewards (
    id SERIAL PRIMARY KEY,
    block_id BIGINT REFERENCES blocks(id) ON DELETE CASCADE,
    receiver TEXT NOT NULL,
    amount BIGINT NOT NULL,
    type TEXT,
    timestamp TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS holders (
    address TEXT PRIMARY KEY,
    balance BIGINT DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stats (
    id INT PRIMARY KEY DEFAULT 1,
    height BIGINT DEFAULT 0,
    total_supply BIGINT DEFAULT 0,
    total_txs BIGINT DEFAULT 0,
    difficulty TEXT,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT one_row CHECK (id = 1)
);

-- 2. TRiggers for Automated Balance Tracking

-- Function to update balance on Transaction
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

-- Function to update balance on Reward
CREATE OR REPLACE FUNCTION update_holder_balance_rew()
RETURNS TRIGGER AS $$
BEGIN
    -- Update Receiver (+ amount)
    INSERT INTO holders (address, balance)
    VALUES (NEW.receiver, NEW.amount)
    ON CONFLICT (address) DO UPDATE
    SET balance = holders.balance + EXCLUDED.balance,
        last_updated = NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach Triggers
DROP TRIGGER IF EXISTS tr_update_bal_tx ON transactions;
CREATE TRIGGER tr_update_bal_tx
AFTER INSERT ON transactions
FOR EACH ROW EXECUTE FUNCTION update_holder_balance_tx();

DROP TRIGGER IF EXISTS tr_update_bal_rew ON rewards;
CREATE TRIGGER tr_update_bal_rew
AFTER INSERT ON rewards
FOR EACH ROW EXECUTE FUNCTION update_holder_balance_rew();

-- Enable Realtime for all tables
ALTER PUBLICATION supabase_realtime ADD TABLE blocks, transactions, rewards, stats;
