"""adding user roles

Revision ID: a4f5b25fbab1
Revises: 2456d90a1b95
Create Date: 2021-11-30 17:33:42.035659

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4f5b25fbab1'
down_revision = '2456d90a1b95'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # with op.batch_alter_table('user', schema=None) as batch_op:
    #     batch_op.add_column(sa.Column('role_id', sa.Integer(), nullable=True))
    #     batch_op.create_foreign_key('role_id', 'roles', ['role_id'], ['id'])

    # ### end Alembic commands ###
    pass

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # with op.batch_alter_table('user', schema=None) as batch_op:
    #     batch_op.drop_constraint(None, type_='foreignkey')
    #     batch_op.drop_column('role_id')
    pass
    # ### end Alembic commands ###
