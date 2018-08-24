"""empty message

Revision ID: 73fd7bb2eb2b
Revises: a8bedc48b160
Create Date: 2018-08-18 08:15:45.379569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73fd7bb2eb2b'
down_revision = 'a8bedc48b160'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('node', sa.Column('need', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('node', 'need')
    # ### end Alembic commands ###