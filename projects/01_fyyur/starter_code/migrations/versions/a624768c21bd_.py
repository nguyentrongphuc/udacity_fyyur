"""empty message

Revision ID: a624768c21bd
Revises: e3a9a7bda6a1
Create Date: 2023-04-17 17:26:23.709835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a624768c21bd'
down_revision = 'e3a9a7bda6a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.drop_column('id')

    # ### end Alembic commands ###
