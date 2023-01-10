"""add colume to posts table

Revision ID: 20cfadfef47f
Revises: b1d85c9aa316
Create Date: 2023-01-10 10:01:41.368984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20cfadfef47f'
down_revision = 'b1d85c9aa316'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
