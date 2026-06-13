"""add_settings_fields_to_farmer

Revision ID: 0a3026b55e8d
Revises: 501adc0c3267
Create Date: 2026-06-13 08:36:34.184233

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a3026b55e8d'
down_revision: Union[str, Sequence[str], None] = '501adc0c3267'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('farmers', sa.Column('theme_preference', sa.String(length=50), server_default='dark', nullable=True))
    op.add_column('farmers', sa.Column('email_notifications', sa.Integer(), server_default='1', nullable=True))
    op.add_column('farmers', sa.Column('push_notifications', sa.Integer(), server_default='1', nullable=True))
    op.add_column('farmers', sa.Column('default_crop', sa.String(length=100), nullable=True))
    op.add_column('farmers', sa.Column('default_soil_type', sa.String(length=100), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('farmers', 'default_soil_type')
    op.drop_column('farmers', 'default_crop')
    op.drop_column('farmers', 'push_notifications')
    op.drop_column('farmers', 'email_notifications')
    op.drop_column('farmers', 'theme_preference')
