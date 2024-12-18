COMPETITIONS = """
CREATE TABLE {schema}.{table} (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    area JSONB NOT NULL,
    code VARCHAR(50),
    type VARCHAR(50),
    emblem VARCHAR(255),
    plan VARCHAR(50),
    current_season JSONB NOT NULL,
    number_of_available_seasons INT NOT NULL,
    last_updated TIMESTAMP NOT NULL,
    load_timestamp TIMESTAMP NOT NULL
);
"""

TEAMS = """
CREATE TABLE {schema}.{table} (
    id SERIAL PRIMARY KEY,
    area JSONB NOT NULL,
    competition_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(255) NOT NULL,
    tla VARCHAR(255) NOT NULL,
    crest VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    founded FLOAT,
    club_colors VARCHAR(255),
    venue VARCHAR(255),
    running_competitions JSONB,
    coach JSONB,
    squad JSONB,
    staff JSONB,
    last_updated TIMESTAMP NOT NULL,
    load_timestamp TIMESTAMP NOT NULL,
    UNIQUE (competition_id, team_id)
);
"""

COMPETITIONS_STANDINGS = """
CREATE TABLE {schema}.{table} (
    id SERIAL PRIMARY KEY,
    position INTEGER NOT NULL,
    team JSONB NOT NULL,
    played_games INTEGER NOT NULL,
    form VARCHAR(255),
    won INTEGER NOT NULL,
    draw INTEGER NOT NULL,
    lost INTEGER NOT NULL,
    points INTEGER NOT NULL,
    goals_for INTEGER NOT NULL,
    goals_against INTEGER NOT NULL,
    goal_difference INTEGER NOT NULL,
    competition_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    season_info JSONB,
    load_timestamp TIMESTAMP NOT NULL,
    UNIQUE (competition_id, position, season)
);
"""

TRUNCATE_TABLE = """
truncate table {schema}.{table};
"""