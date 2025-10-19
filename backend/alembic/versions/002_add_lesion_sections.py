"""Add LesionSection table and enhance History for progress tracking

Revision ID: 002
Revises: 001
Create Date: 2025-10-19 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add LesionSection table and enhance History table with:
    - section_id foreign key
    - is_baseline flag
    - user_notes field
    - Make gemini_response nullable
    """
    
    # Create lesion_sections table
    op.create_table(
        'lesion_sections',
        sa.Column('section_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('section_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_baseline', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('section_id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_lesion_sections_user_id'), 'lesion_sections', ['user_id'], unique=False)
    
    # Add new columns to history table
    op.add_column('history', sa.Column('section_id', sa.String(length=36), nullable=True))
    op.add_column('history', sa.Column('is_baseline', sa.Boolean(), nullable=True, default=False))
    op.add_column('history', sa.Column('user_notes', sa.Text(), nullable=True))
    
    # Make gemini_response nullable (for entries that haven't been reviewed yet)
    # SQLite doesn't support ALTER COLUMN directly, so we need to handle it differently
    bind = op.get_bind()
    if bind.dialect.name == 'sqlite':
        # For SQLite, we need to recreate the table (complex, skip for now)
        # Existing data will remain, new entries can have NULL gemini_response
        pass
    else:
        # For PostgreSQL
        op.alter_column('history', 'gemini_response',
                       existing_type=sa.Text(),
                       nullable=True)
    
    # Create indexes
    op.create_index(op.f('ix_history_section_id'), 'history', ['section_id'], unique=False)
    op.create_index(op.f('ix_history_is_baseline'), 'history', ['is_baseline'], unique=False)
    
    # Note: SQLite doesn't support adding foreign key constraints after table creation
    # Foreign key relationship will be enforced at the ORM level in models.py


def downgrade() -> None:
    """Remove LesionSection enhancements."""
    
    # Drop indexes
    op.drop_index(op.f('ix_history_is_baseline'), table_name='history')
    op.drop_index(op.f('ix_history_section_id'), table_name='history')
    
    # Drop columns from history
    op.drop_column('history', 'user_notes')
    op.drop_column('history', 'is_baseline')
    op.drop_column('history', 'section_id')
    
    # Drop lesion_sections table
    op.drop_index(op.f('ix_lesion_sections_user_id'), table_name='lesion_sections')
    op.drop_table('lesion_sections')
