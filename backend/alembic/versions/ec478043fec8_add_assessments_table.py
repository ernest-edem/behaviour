"""add assessments table

Revision ID: ec478043fec8
Revises: 87a70be972d4
Create Date: 2026-06-09 19:33:46.024390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ec478043fec8'
down_revision: Union[str, Sequence[str], None] = '87a70be972d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('assessments', sa.Column('gender', sa.String(length=20), nullable=True))
    op.add_column('assessments', sa.Column('weight', sa.Float(), nullable=True))
    op.add_column('assessments', sa.Column('height', sa.Float(), nullable=True))
    op.add_column('assessments', sa.Column('diet_quality', sa.Integer(), nullable=True))
    op.add_column('assessments', sa.Column('alcohol_use', sa.Integer(), nullable=True))
    op.add_column('assessments', sa.Column('blood_glucose', sa.Float(), nullable=True))
    op.add_column('assessments', sa.Column('medication_adherence', sa.Integer(), nullable=True))
    op.add_column('assessments', sa.Column('emotional_wellbeing', sa.Integer(), nullable=True))

    op.execute("UPDATE assessments SET alcohol_use = alcohol WHERE alcohol_use IS NULL")
    op.execute("UPDATE assessments SET blood_glucose = glucose_level WHERE blood_glucose IS NULL")
    op.execute("UPDATE assessments SET gender = 'unspecified' WHERE gender IS NULL")
    op.execute("UPDATE assessments SET weight = 70.0 WHERE weight IS NULL")
    op.execute("UPDATE assessments SET height = 170.0 WHERE height IS NULL")
    op.execute("UPDATE assessments SET diet_quality = 5 WHERE diet_quality IS NULL")
    op.execute("UPDATE assessments SET medication_adherence = 5 WHERE medication_adherence IS NULL")
    op.execute("UPDATE assessments SET emotional_wellbeing = 5 WHERE emotional_wellbeing IS NULL")

    op.alter_column('assessments', 'gender', nullable=False)
    op.alter_column('assessments', 'weight', nullable=False)
    op.alter_column('assessments', 'height', nullable=False)
    op.alter_column('assessments', 'diet_quality', nullable=False)
    op.alter_column('assessments', 'alcohol_use', nullable=False)
    op.alter_column('assessments', 'blood_glucose', nullable=False)
    op.alter_column('assessments', 'medication_adherence', nullable=False)
    op.alter_column('assessments', 'emotional_wellbeing', nullable=False)

    op.alter_column(
        'assessments',
        'created_at',
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using='created_at AT TIME ZONE \'UTC\'',
    )
    op.drop_column('assessments', 'glucose_level')
    op.drop_column('assessments', 'alcohol')

    op.alter_column(
        'predictions',
        'created_at',
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using='created_at AT TIME ZONE \'UTC\'',
    )
    op.alter_column(
        'users',
        'created_at',
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using='created_at AT TIME ZONE \'UTC\'',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'users',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        'predictions',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )

    op.add_column('assessments', sa.Column('alcohol', sa.Integer(), nullable=True))
    op.add_column('assessments', sa.Column('glucose_level', sa.Float(), nullable=True))
    op.execute("UPDATE assessments SET alcohol = alcohol_use WHERE alcohol IS NULL")
    op.execute("UPDATE assessments SET glucose_level = blood_glucose WHERE glucose_level IS NULL")
    op.alter_column('assessments', 'alcohol', nullable=False)
    op.alter_column('assessments', 'glucose_level', nullable=False)

    op.alter_column(
        'assessments',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.drop_column('assessments', 'emotional_wellbeing')
    op.drop_column('assessments', 'medication_adherence')
    op.drop_column('assessments', 'blood_glucose')
    op.drop_column('assessments', 'alcohol_use')
    op.drop_column('assessments', 'diet_quality')
    op.drop_column('assessments', 'height')
    op.drop_column('assessments', 'weight')
    op.drop_column('assessments', 'gender')
