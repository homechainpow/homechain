-- HomeChain Supabase Schema

-- 1. Blocks Table
CREATE TABLE IF NOT EXISTS blocks (
    id BIGINT PRIMARY KEY, -- block index
    hash TEXT UNIQUE NOT NULL,
    prev_hash TEXT,
    timestamp TIMESTAMPTZ NOT NULL,
    validator TEXT NOT NULL,
    tx_count INT DEFAULT 0,
    reward_count INT DEFAULT 0,
    target TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Transactions Table
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

-- 3. Rewards Table
CREATE TABLE IF NOT EXISTS rewards (
    id SERIAL PRIMARY KEY,
    block_id BIGINT REFERENCES blocks(id) ON DELETE CASCADE,
    receiver TEXT NOT NULL,
    amount BIGINT NOT NULL,
    type TEXT, -- 'finder' or 'bonus'
    timestamp TIMESTAMPTZ NOT NULL
);

-- 4. Holders Table (Pre-calculated for fast lookup/ranking)
CREATE TABLE IF NOT EXISTS holders (
    address TEXT PRIMARY KEY,
    balance BIGINT DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Network Stats (Single row)
CREATE TABLE IF NOT EXISTS stats (
    id INT PRIMARY KEY DEFAULT 1,
    height BIGINT DEFAULT 0,
    total_supply BIGINT DEFAULT 0,
    total_txs BIGINT DEFAULT 0,
    difficulty TEXT,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT one_row CHECK (id = 1)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_tx_sender ON transactions(sender);
CREATE INDEX IF NOT EXISTS idx_tx_receiver ON transactions(receiver);
CREATE INDEX IF NOT EXISTS idx_rewards_receiver ON rewards(receiver);
CREATE INDEX IF NOT EXISTS idx_holders_balance ON holders(balance DESC);
