"""Drop unique constraint from users.password

Revision ID: 0001_drop_password_unique
Revises: 
Create Date: 2026-05-25 23:00:00.000000
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = '0001_drop_password_unique'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute('ALTER TABLE users DROP CONSTRAINT IF EXISTS users_password_key')


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute('ALTER TABLE users ADD CONSTRAINT users_password_key UNIQUE (password)')