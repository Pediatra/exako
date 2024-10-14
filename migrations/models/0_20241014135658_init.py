from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "term" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "expression" VARCHAR(256) NOT NULL,
    "language" VARCHAR(7) NOT NULL,
    "additional_content" JSONB,
    CONSTRAINT "uid_term_express_50db46" UNIQUE ("expression", "language")
);
CREATE INDEX IF NOT EXISTS "idx_term_express_50db46" ON "term" ("expression", "language");
CREATE TABLE IF NOT EXISTS "termexample" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "language" VARCHAR(7) NOT NULL,
    "content" VARCHAR(256) NOT NULL,
    "level" VARCHAR(2),
    "additional_content" JSONB
);
CREATE TABLE IF NOT EXISTS "termexampletranslation" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "language" VARCHAR(7) NOT NULL,
    "translation" VARCHAR(256) NOT NULL,
    "term_example_id" INT NOT NULL REFERENCES "termexample" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_termexample_languag_d18c58" UNIQUE ("language", "term_example_id")
);
CREATE TABLE IF NOT EXISTS "termimage" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "image_url" VARCHAR(256) NOT NULL,
    "term_id" INT NOT NULL UNIQUE REFERENCES "term" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "termlexical" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "value" VARCHAR(256),
    "type" SMALLINT NOT NULL,
    "additional_content" JSONB,
    "term_id" INT NOT NULL REFERENCES "term" ("id") ON DELETE CASCADE,
    "term_value_id" INT REFERENCES "term" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "termdefinition" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "part_of_speech" SMALLINT NOT NULL,
    "content" VARCHAR(712) NOT NULL,
    "level" VARCHAR(2),
    "additional_content" JSONB,
    "term_id" INT NOT NULL REFERENCES "term" ("id") ON DELETE CASCADE,
    "term_lexical_id" INT REFERENCES "termlexical" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "termdefinitiontranslation" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "language" VARCHAR(2) NOT NULL,
    "translation" VARCHAR(712) NOT NULL,
    "meaning" VARCHAR(256) NOT NULL,
    "term_definition_id" INT NOT NULL REFERENCES "termdefinition" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_termdefinit_languag_0bfa4f" UNIQUE ("language", "term_definition_id")
);
CREATE TABLE IF NOT EXISTS "termexamplelink" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "highlight" int[][] NOT NULL,
    "term_id" INT REFERENCES "term" ("id") ON DELETE CASCADE,
    "term_definition_id" INT REFERENCES "termdefinition" ("id") ON DELETE CASCADE,
    "term_example_id" INT NOT NULL REFERENCES "termexample" ("id") ON DELETE CASCADE,
    "term_lexical_id" INT REFERENCES "termlexical" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_termexample_term_id_f089e7" UNIQUE ("term_id", "term_example_id"),
    CONSTRAINT "uid_termexample_term_de_d46382" UNIQUE ("term_definition_id", "term_example_id"),
    CONSTRAINT "uid_termexample_term_le_59b641" UNIQUE ("term_lexical_id", "term_example_id")
);
CREATE TABLE IF NOT EXISTS "termpronunciation" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "phonetic" VARCHAR(256) NOT NULL,
    "audio_url" VARCHAR(256),
    "term_id" INT  UNIQUE REFERENCES "term" ("id") ON DELETE CASCADE,
    "term_lexical_id" INT  UNIQUE REFERENCES "termlexical" ("id") ON DELETE CASCADE,
    "term_example_id" INT  UNIQUE REFERENCES "termexample" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "exercise" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "language" VARCHAR(7) NOT NULL,
    "type" SMALLINT NOT NULL,
    "level" VARCHAR(2),
    "additional_content" JSONB,
    "term_id" INT REFERENCES "term" ("id") ON DELETE CASCADE,
    "term_definition_id" INT REFERENCES "termdefinition" ("id") ON DELETE CASCADE,
    "term_example_id" INT REFERENCES "termexample" ("id") ON DELETE CASCADE,
    "term_image_id" INT REFERENCES "termimage" ("id") ON DELETE CASCADE,
    "term_lexical_id" INT REFERENCES "termlexical" ("id") ON DELETE CASCADE,
    "term_pronunciation_id" INT REFERENCES "termpronunciation" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "user" (
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "hashed_password" VARCHAR(1024) NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "is_superuser" BOOL NOT NULL  DEFAULT False,
    "is_verified" BOOL NOT NULL  DEFAULT False,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50),
    "native_language" VARCHAR(7) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_user_email_1b4f1c" ON "user" ("email");
CREATE TABLE IF NOT EXISTS "exercisehistory" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "correct" BOOL NOT NULL,
    "response" JSONB,
    "request" JSONB,
    "exercise_id" INT NOT NULL REFERENCES "exercise" ("id") ON DELETE NO ACTION,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE NO ACTION
);
CREATE TABLE IF NOT EXISTS "cardset" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(256) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_review" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "pinned" BOOL NOT NULL  DEFAULT False,
    "language" VARCHAR(7),
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "card" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "note" TEXT,
    "created_at" DATE NOT NULL,
    "last_review" DATE NOT NULL,
    "cardset_id" INT NOT NULL REFERENCES "cardset" ("id") ON DELETE CASCADE,
    "term_id" INT NOT NULL REFERENCES "term" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
