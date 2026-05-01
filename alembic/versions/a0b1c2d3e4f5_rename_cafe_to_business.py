"""rename_cafe_to_business

Revision ID: a0b1c2d3e4f5
Revises: 74e73a13ec77
Create Date: 2026-05-01 11:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a0b1c2d3e4f5'
down_revision: Union[str, Sequence[str], None] = '74e73a13ec77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename tables
    op.rename_table('cafes', 'businesses')
    
    # Rename columns in other tables
    op.alter_column('users', 'cafe_id', new_column_name='business_id')
    op.alter_column('missions', 'cafe_id', new_column_name='business_id')
    op.alter_column('transactions', 'cafe_id', new_column_name='business_id')
    op.alter_column('redeem_tokens', 'cafe_id', new_column_name='business_id')
    op.alter_column('portfolio_items', 'hide_cafe_name', new_column_name='hide_business_name')
    
    # Add category to businesses
    op.add_column('businesses', sa.Column('category', sa.String(), nullable=True))

    # Rename CAFE_ADMIN to BUSINESS_ADMIN in userrole enum (PostgreSQL specific)
    # For SQLite or others, a simple UPDATE would be needed, but since Postgres uses native enums:
    op.execute("ALTER TYPE userrole RENAME VALUE 'CAFE_ADMIN' TO 'BUSINESS_ADMIN'")



def downgrade() -> None:
    # Remove category
    op.drop_column('businesses', 'category')
    
    # Rename columns back
    op.alter_column('redeem_tokens', 'business_id', new_column_name='cafe_id')
    op.alter_column('transactions', 'business_id', new_column_name='cafe_id')
    op.alter_column('missions', 'business_id', new_column_name='cafe_id')
    op.alter_column('users', 'business_id', new_column_name='cafe_id')
    op.alter_column('portfolio_items', 'hide_business_name', new_column_name='hide_cafe_name')
    
    # Rename tables back
    op.rename_table('businesses', 'cafes')

    # Rename enum back
    op.execute("ALTER TYPE userrole RENAME VALUE 'BUSINESS_ADMIN' TO 'CAFE_ADMIN'")
