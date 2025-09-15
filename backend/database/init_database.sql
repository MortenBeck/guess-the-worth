-- Database initialization script for Guess The Worth application
-- Based on database.txt schema

-- Enable UUID extension (commonly used for IDs)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    auth0_sub VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('buyer', 'seller', 'admin')) NOT NULL DEFAULT 'buyer',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Artworks table
CREATE TABLE IF NOT EXISTS artworks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    secret_threshold DECIMAL(10,2) NOT NULL,
    current_highest_bid DECIMAL(10,2) DEFAULT 0.00,
    description TEXT,
    image_url VARCHAR(1000),
    status VARCHAR(20) CHECK (status IN ('active', 'sold')) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bids table
CREATE TABLE IF NOT EXISTS bids (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    artwork_id UUID NOT NULL REFERENCES artworks(id) ON DELETE CASCADE,
    bidder_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    bid_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_winning BOOLEAN DEFAULT FALSE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_auth0_sub ON users(auth0_sub);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_artworks_seller_id ON artworks(seller_id);
CREATE INDEX IF NOT EXISTS idx_artworks_status ON artworks(status);
CREATE INDEX IF NOT EXISTS idx_bids_artwork_id ON bids(artwork_id);
CREATE INDEX IF NOT EXISTS idx_bids_bidder_id ON bids(bidder_id);
CREATE INDEX IF NOT EXISTS idx_bids_bid_time ON bids(bid_time);

-- Create a trigger to update current_highest_bid and is_winning when new bids are placed
CREATE OR REPLACE FUNCTION update_highest_bid_and_winning()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the current_highest_bid for the artwork
    UPDATE artworks
    SET current_highest_bid = (
        SELECT MAX(amount)
        FROM bids
        WHERE artwork_id = NEW.artwork_id
    )
    WHERE id = NEW.artwork_id;

    -- Update the is_winning field for the new bid
    UPDATE bids
    SET is_winning = (
        NEW.amount >= (SELECT secret_threshold FROM artworks WHERE id = NEW.artwork_id)
    )
    WHERE id = NEW.id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_highest_bid_and_winning
    AFTER INSERT ON bids
    FOR EACH ROW
    EXECUTE FUNCTION update_highest_bid_and_winning();

-- Insert some sample data for testing (optional)
-- Sample admin user
INSERT INTO users (auth0_sub, email, name, role)
VALUES ('auth0|admin', 'admin@example.com', 'Admin User', 'admin')
ON CONFLICT (auth0_sub) DO NOTHING;

-- Sample seller (artist)
INSERT INTO users (auth0_sub, email, name, role)
VALUES ('auth0|artist1', 'artist1@example.com', 'Artist One', 'seller')
ON CONFLICT (auth0_sub) DO NOTHING;

-- Sample buyer
INSERT INTO users (auth0_sub, email, name, role)
VALUES ('auth0|buyer1', 'buyer1@example.com', 'Buyer One', 'buyer')
ON CONFLICT (auth0_sub) DO NOTHING;

COMMIT;