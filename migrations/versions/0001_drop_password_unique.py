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
        # Bootstrap schema for fresh databases.
        op.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(128) NOT NULL UNIQUE,
                email_id VARCHAR(128) NOT NULL UNIQUE,
                password VARCHAR(512) NOT NULL,
                created_on TIMESTAMP WITHOUT TIME ZONE
            )
        ''')
        op.execute('CREATE INDEX IF NOT EXISTS ix_users_username ON users (username)')
        op.execute('CREATE INDEX IF NOT EXISTS ix_users_email_id ON users (email_id)')

        op.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title VARCHAR(140) NOT NULL,
                description TEXT,
                due_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                priority VARCHAR(50) NOT NULL DEFAULT 'Low',
                status VARCHAR(50) NOT NULL DEFAULT 'To Do',
                assignee INTEGER NOT NULL REFERENCES users(id),
                created_on TIMESTAMP WITHOUT TIME ZONE
            )
        ''')

        # Keep compatibility with older schema variants.
        op.execute('ALTER TABLE users DROP CONSTRAINT IF EXISTS users_password_key')
        op.execute('ALTER TABLE users ALTER COLUMN password TYPE VARCHAR(512)')


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute('ALTER TABLE users ALTER COLUMN password TYPE VARCHAR(128)')
        op.execute('ALTER TABLE users ADD CONSTRAINT users_password_key UNIQUE (password)')