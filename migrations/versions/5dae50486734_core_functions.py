"""core functions

Revision ID: 5dae50486734
Revises: 1f6e85ee7053
Create Date: 2024-10-16 15:57:09.557143

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5dae50486734'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS unaccent;')
    op.execute('''
        CREATE OR REPLACE FUNCTION clean_text(text_value TEXT)
        RETURNS TEXT AS
        $$
        BEGIN
            RETURN lower(unaccent(text_value));
        END;
        $$
        LANGUAGE plpgsql
        IMMUTABLE;
    ''')

def downgrade():
    op.execute('DROP FUNCTION IF EXISTS clean_text(text);')
    op.execute('DROP EXTENSION IF EXISTS unaccent;')

