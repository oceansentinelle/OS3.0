"""Add reference_entities table for Phase 2

Revision ID: 001
Revises: 
Create Date: 2026-04-18 00:00:00

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
    # Create reference_entities table for Phase 2 (SHOM, INSEE)
    op.create_table(
        'reference_entities',
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('source_code', sa.String(50), nullable=False),
        sa.Column('external_id', sa.String(255), nullable=False),
        sa.Column('record_type', sa.String(100), nullable=False),
        sa.Column('observed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('payload', postgresql.JSONB, nullable=False),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.UniqueConstraint('source_code', 'external_id', name='uq_reference_entities_source_external')
    )
    
    # Indexes
    op.create_index('idx_reference_entities_source', 'reference_entities', ['source_code'])
    op.create_index('idx_reference_entities_type', 'reference_entities', ['record_type'])
    op.create_index('idx_reference_entities_observed', 'reference_entities', ['observed_at'])
    
    # Comment
    op.execute("""
        COMMENT ON TABLE reference_entities IS 
        'Entités de référence Phase 2 (SHOM métadonnées, INSEE géo/sirene)'
    """)


def downgrade() -> None:
    op.drop_table('reference_entities')
