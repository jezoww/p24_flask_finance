"""from string to float

Revision ID: 422b7a5efbf1
Revises: 
Create Date: 2024-07-14 22:51:02.027992

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '422b7a5efbf1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('e_wallets', schema=None) as batch_op:
        batch_op.alter_column('balance',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('e_wallets', schema=None) as batch_op:
        batch_op.alter_column('balance',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=False)

    # ### end Alembic commands ###
