"""add last few colums

Revision ID: 055e22f6b3b5
Revises: b09d203bbc8e
Create Date: 2023-01-10 10:40:37.195178

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '055e22f6b3b5'
down_revision = 'b09d203bbc8e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column(
        'published', sa.Boolean(), nullable=False, server_default='TRUE'),)
    op.add_column('posts', sa.Column(
        'created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),)

    pass


def downgrade() -> None:
    op.drop_column('posts', 'published')
    op.drop_column('posts', 'created_at')
    pass
