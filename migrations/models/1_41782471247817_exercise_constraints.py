from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE UNIQUE INDEX unique_order_sentence
        ON exercise (type, language, term_example_id)
        WHERE type = 0;

        CREATE UNIQUE INDEX unique_listen_term
        ON exercise (type, language, term_id, term_pronunciation_id)
        WHERE type = 1;

        CREATE UNIQUE INDEX unique_listen_term_lexical
        ON exercise (type, language, term_lexical_id, term_pronunciation_id)
        WHERE type = 1;

        CREATE UNIQUE INDEX unique_listen_term_mchoice
        ON exercise (type, language, term_id, term_pronunciation_id)
        WHERE type = 2;

        CREATE UNIQUE INDEX unique_listen_sentence
        ON exercise (type, language, term_example_id, term_pronunciation_id)
        WHERE type = 3;

        CREATE UNIQUE INDEX unique_speak_term
        ON exercise (type, language, term_id)
        WHERE type = 4;

        CREATE UNIQUE INDEX unique_speak_term_lexical
        ON exercise (type, language, term_lexical_id)
        WHERE type = 4;

        CREATE UNIQUE INDEX unique_speak_sentence
        ON exercise (type, language, term_example_id)
        WHERE type = 5;

        CREATE UNIQUE INDEX unique_term_mchoice
        ON exercise (type, language, term_id, term_example_id)
        WHERE type = 6;

        CREATE UNIQUE INDEX unique_term_lexical_mchoice
        ON exercise (type, language, term_example_id, term_lexical_id)
        WHERE type = 6;

        CREATE UNIQUE INDEX unique_term_definition_mchoice
        ON exercise (type, language, term_definition_id, term_id)
        WHERE type = 7;

        CREATE UNIQUE INDEX unique_term_image_mchoice
        ON exercise (type, language, term_id, term_image_id, term_pronunciation_id)
        WHERE type = 8;

        CREATE UNIQUE INDEX unique_term_image_mchoice_text
        ON exercise (type, language, term_id, term_image_id)
        WHERE type = 9;

        CREATE UNIQUE INDEX unique_term_conection
        ON exercise (type, language, term_id)
        WHERE type = 10;

    """

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """