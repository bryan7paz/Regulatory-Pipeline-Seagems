"""initial schema

Revision ID: 0767ea201e62
Revises: 
Create Date: 2026-09-17 13:19:47.701330

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0767ea201e62'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    assunto_enum = sa.Enum("SEG", "INC", "COM", "NAV", "CON", "TRI", "AMB", "NAU", "IMO",
                           name="assunto_enum")
    aplicacao_enum = sa.Enum("D", "I", "NP", name="aplicacao_enum")
    status_enum = sa.Enum("R", "N", name="status_enum")

    assunto_enum.create(op.get_bind(), checkfirst=True)
    aplicacao_enum.create(op.get_bind(), checkfirst=True)
    status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "regulatory_analysis",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("source_id", sa.String),
        sa.Column("source_name", sa.String),
        sa.Column("documento_hash", sa.String, index=True),
        sa.Column("url_origem", sa.Text),
        sa.Column("data_publicacao", sa.Date, nullable=True),
        sa.Column("entrada_em_vigor", sa.Date, nullable=True),
        sa.Column("requisito", sa.String, nullable=True),
        sa.Column("norma", sa.String, nullable=True),
        sa.Column("assunto", assunto_enum, nullable=True),
        sa.Column("aplicacao", aplicacao_enum, nullable=True),
        sa.Column("status", status_enum, nullable=True),
        sa.Column("item", sa.String, nullable=True),
        sa.Column("itens_modificados", sa.Text, nullable=True),
        sa.Column("acao_sugerida", sa.Text, nullable=True),
        sa.Column("status_validacao", sa.String, server_default="pendente"),
        sa.Column("raw_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("validated_at", sa.DateTime, nullable=True),
        sa.Column("validated_by", sa.String, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("regulatory_analysis")
    sa.Enum(name="status_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="aplicacao_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="assunto_enum").drop(op.get_bind(), checkfirst=True)