
CREATE TABLE IF NOT EXISTS servers(
    id TEXT PRIMARY KEY,
    users JSON,
    deathrolls JSON,
    standardrolls JSON
)
