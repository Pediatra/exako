"""exercise constraints

Revision ID: e72fef13c0ed
Revises: 5dae50486734
Create Date: 2024-10-16 20:56:53.828298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e72fef13c0ed'
down_revision: Union[str, None] = '5dae50486734'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = ['1f6e85ee7053']

def upgrade():
    # Criar índices únicos conforme o SQL fornecido
    op.create_index(
        'unique_order_sentence', 
        'exercise', 
        ['type', 'language', 'term_example_id'], 
        unique=True, 
        postgresql_where=sa.text('type = 0')
    )
    
    op.create_index(
        'unique_listen_term', 
        'exercise', 
        ['type', 'language', 'term_id', 'term_pronunciation_id'], 
        unique=True, 
        postgresql_where=sa.text('type = 1')
    )
    
    op.create_index(
        'unique_listen_term_lexical', 
        'exercise', 
        ['type', 'language', 'term_lexical_id', 'term_pronunciation_id'], 
        unique=True, 
        postgresql_where=sa.text('type = 1')
    )
    
    op.create_index(
        'unique_listen_term_mchoice', 
        'exercise', 
        ['type', 'language', 'term_id', 'term_pronunciation_id'], 
        unique=True, 
        postgresql_where=sa.text('type = 2')
    )
    
    op.create_index(
        'unique_listen_sentence', 
        'exercise', 
        ['type', 'language', 'term_example_id', 'term_pronunciation_id'], 
        unique=True, 
        postgresql_where=sa.text('type = 3')
    )
    
    op.create_index(
        'unique_speak_term', 
        'exercise', 
        ['type', 'language', 'term_id'], 
        unique=True, 
        postgresql_where=sa.text('type = 4')
    )
    
    op.create_index(
        'unique_speak_term_lexical', 
        'exercise', 
        ['type', 'language', 'term_lexical_id'], 
        unique=True, 
        postgresql_where=sa.text('type = 4')
    )
    
    op.create_index(
        'unique_speak_sentence', 
        'exercise', 
        ['type', 'language', 'term_example_id'], 
        unique=True, 
        postgresql_where=sa.text('type = 5')
    )
    
    op.create_index(
        'unique_term_mchoice', 
        'exercise', 
        ['type', 'language', 'term_id', 'term_example_id'], 
        unique=True, 
        postgresql_where=sa.text('type = 6')
    )
    
    op.create_index(
        'unique_term_lexical_mchoice', 
        'exercise', 
        ['type', 'language', 'term_example_id', 'term_lexical_id'], 
        unique=True, 
        postgresql_where=sa.text('type = 6')
    )
    
    op.create_index(
        'unique_term_definition_mchoice', 
        'exercise', 
        ['type', 'language', 'term_definition_id', 'term_id'], 
        unique=True, 
        postgresql_where=sa.text('type = 7')
    )
    
    op.create_index(
        'unique_term_image_mchoice', 
        'exercise', 
        ['type', 'language', 'term_id', 'term_image_id', 'term_pronunciation_id'], 
        unique=True, 
        postgresql_where=sa.text('type = 8')
    )
    
    op.create_index(
        'unique_term_image_mchoice_text', 
        'exercise', 
        ['type', 'language', 'term_id', 'term_image_id'], 
        unique=True, 
        postgresql_where=sa.text('type = 9')
    )
    
    op.create_index(
        'unique_term_conection', 
        'exercise', 
        ['type', 'language', 'term_id'], 
        unique=True, 
        postgresql_where=sa.text('type = 10')
    )

def downgrade():
    # Remover os índices na reversão
    op.drop_index('unique_order_sentence', table_name='exercise')
    op.drop_index('unique_listen_term', table_name='exercise')
    op.drop_index('unique_listen_term_lexical', table_name='exercise')
    op.drop_index('unique_listen_term_mchoice', table_name='exercise')
    op.drop_index('unique_listen_sentence', table_name='exercise')
    op.drop_index('unique_speak_term', table_name='exercise')
    op.drop_index('unique_speak_term_lexical', table_name='exercise')
    op.drop_index('unique_speak_sentence', table_name='exercise')
    op.drop_index('unique_term_mchoice', table_name='exercise')
    op.drop_index('unique_term_lexical_mchoice', table_name='exercise')
    op.drop_index('unique_term_definition_mchoice', table_name='exercise')
    op.drop_index('unique_term_image_mchoice', table_name='exercise')
    op.drop_index('unique_term_image_mchoice_text', table_name='exercise')
    op.drop_index('unique_term_conection', table_name='exercise')
