-- 1. Groups table
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO groups (name) VALUES
    ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

-- 2. Contacts table
CREATE TABLE IF NOT EXISTS contacts (
    id           SERIAL PRIMARY KEY,
    first_name   VARCHAR(50)  NOT NULL,
    last_name    VARCHAR(50),
    phone_number VARCHAR(20),
    email        VARCHAR(100),
    birthday     DATE,
    group_id     INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    created_at   TIMESTAMP DEFAULT NOW()
);

-- 3. Phones table (multiple phones per contact)
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
);