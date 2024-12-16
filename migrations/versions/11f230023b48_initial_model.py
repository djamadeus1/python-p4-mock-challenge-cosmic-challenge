"""initial model

Revision ID: 11f230023b48
Revises: 
Create Date: 2024-12-16 12:23:36.837783

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11f230023b48'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('planets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('distance_from_earth', sa.Integer(), nullable=True),
    sa.Column('nearest_star', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_planets'))
    )
    op.create_table('scientists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('field_of_study', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_scientists'))
    )
    op.create_table('missions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('scientist_id', sa.Integer(), nullable=False),
    sa.Column('planet_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['planet_id'], ['planets.id'], name=op.f('fk_missions_planet_id_planets')),
    sa.ForeignKeyConstraint(['scientist_id'], ['scientists.id'], name=op.f('fk_missions_scientist_id_scientists')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_missions'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('missions')
    op.drop_table('scientists')
    op.drop_table('planets')
    # ### end Alembic commands ###