"""Baseline migration

Revision ID: 2bf33653ce95
Revises: 
Create Date: 2026-08-11 22:37:54.769332

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2bf33653ce95'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from backend.app.soul.db import _SCHEMA
    for statement in _SCHEMA.split(';'):
        stmt = statement.strip()
        if stmt:
            op.execute(stmt)

def downgrade() -> None:
    tables = [
        "memories", "preferences", "interaction_log", "habits", 
        "sessions", "messages", "action_log", "config", "devices"
    ]
    for table in tables:
        op.execute(f"DROP TABLE IF EXISTS {table}")
