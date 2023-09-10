"""add_server_stuff

Revision ID: 11a59f54d3fc
Revises: be77fc22a5da
Create Date: 2023-09-10 18:00:54.199400

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '11a59f54d3fc'
down_revision: Union[str, None] = 'be77fc22a5da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('server_flavor',
                    sa.Column('name', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('name'),
                    sa.UniqueConstraint('name')
                    )
    op.create_table('server_image',
                    sa.Column('name', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('name'),
                    sa.UniqueConstraint('name')
                    )
    op.create_table('server_network',
                    sa.Column('name', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('name'),
                    sa.UniqueConstraint('name')
                    )
    op.create_unique_constraint(None, 'server_config', ['name'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'server_config', type_='unique')
    op.drop_table('server_network')
    op.drop_table('server_image')
    op.drop_table('server_flavor')
    # ### end Alembic commands ###
