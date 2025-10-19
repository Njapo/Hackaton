"""Add History table for skin disease analysis tracking

Revision ID: 001
Revises: 
Create Date: 2025-10-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create the history table for storing skin disease analysis with embeddings.
    
    Note: This migration works with both SQLite and PostgreSQL.
    For PostgreSQL with pgvector, the extension should be enabled first:
        CREATE EXTENSION IF NOT EXISTS vector;
    """
    # Check if we're using PostgreSQL
    bind = op.get_bind()
    is_postgresql = bind.dialect.name == 'postgresql'
    
    if is_postgresql:
        # Enable pgvector extension for PostgreSQL
        op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create history table
    op.create_table(
        'history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('image_path', sa.String(length=500), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('disease_predictions', sa.JSON(), nullable=False),
        sa.Column('dino_embedding', 
                  postgresql.ARRAY(sa.Float, dimensions=1) if is_postgresql else sa.JSON(), 
                  nullable=True),
        sa.Column('gemini_response', sa.Text(), nullable=False),
        sa.Column('healing_score', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_history_id'), 'history', ['id'], unique=False)
    op.create_index(op.f('ix_history_user_id'), 'history', ['user_id'], unique=False)
    op.create_index(op.f('ix_history_timestamp'), 'history', ['timestamp'], unique=False)
    
    # For PostgreSQL with pgvector, you can add a vector index:
    # op.execute('CREATE INDEX ON history USING ivfflat (dino_embedding vector_cosine_ops) WITH (lists = 100)')


def downgrade() -> None:
    """Drop the history table."""
    op.drop_index(op.f('ix_history_timestamp'), table_name='history')
    op.drop_index(op.f('ix_history_user_id'), table_name='history')
    op.drop_index(op.f('ix_history_id'), table_name='history')
    op.drop_table('history')
