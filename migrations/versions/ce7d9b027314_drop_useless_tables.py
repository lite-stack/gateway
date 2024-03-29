"""insert_server_configs_and_drop_useless_tables

Revision ID: ce7d9b027314
Revises: 11a59f54d3fc
Create Date: 2023-10-10 20:42:29.666832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce7d9b027314'
down_revision: Union[str, None] = '11a59f54d3fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('server_network')
    op.drop_table('server_image')
    op.drop_table('server_flavor')
    op.create_unique_constraint(None, 'server', ['openstack_id'])


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'server', type_='unique')
    op.create_table('server_flavor',
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('name', name='server_flavor_pkey')
    )
    op.create_table('server_image',
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('name', name='server_image_pkey')
    )
    op.create_table('server_network',
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('name', name='server_network_pkey')
    )
    # ### end Alembic commands ###
