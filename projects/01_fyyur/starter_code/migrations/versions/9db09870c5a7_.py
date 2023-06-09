"""empty message

Revision ID: 9db09870c5a7
Revises: 44a7a9a96199
Create Date: 2023-04-17 17:51:56.188089

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9db09870c5a7'
down_revision = '44a7a9a96199'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.Integer(), autoincrement=True, nullable=False))
        batch_op.alter_column('artist_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('venue_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Show', schema=None) as batch_op:
        batch_op.alter_column('venue_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('artist_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_column('id')

    # ### end Alembic commands ###
