"""Pydantic schema for the structured regulatory analysis.

Mirrors the spreadsheet columns:

    Data Publicacao | Entrada Em Vigor | Requisito | Norma | Assunto |
    Aplicacao | Status | Item | Itens Modificados / Objetivos | Acao Sugerida
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Aplicacao(str, Enum):
    ACAO_DIRETA = "D"
    ACAO_INDIRETA = "I"
    NAO_PERTINENTE = "NP"


class Status(str, Enum):
    REVISAO = "R"
    NOVA_VERSAO = "N"


class Assunto(str, Enum):
    SEGURANCA = "SEG"
    INCENDIO = "INC"
    COMUNICACAO = "COM"
    NAVEGACAO = "NAV"
    CONSTRUCAO_NAVAL = "CON"
    TRIPULACAO = "TRI"
    MEIO_AMBIENTE = "AMB"
    NAUFRAGIO = "NAU"
    IMO = "IMO"


class RegulatoryAnalysis(BaseModel):
    """Structured output produced by the LLM."""

    data_publicacao: str | None = Field(
        None, description="Data de elaboração/publicação no formato AAAA-MM-DD"
    )
    entrada_em_vigor: str | None = Field(
        None, description="Data de entrada em vigor no formato AAAA-MM-DD"
    )
    requisito: str | None = Field(None, description="Autoridade/fonte emissora")
    norma: str | None = Field(None, description="Código + título da norma")
    assunto: Assunto | None = Field(None, description="Categoria do assunto (sigla)")
    aplicacao: Aplicacao | None = Field(
        None, description="D (direta), I (indireta) ou NP (não pertinente)"
    )
    status: Status | None = Field(None, description="R (revisão) ou N (nova versão)")
    item: str | None = Field(None, description="Item/trecho específico alterado")
    itens_modificados: str | None = Field(None, description="Descrição do que mudou")
    acao_sugerida: str | None = Field(None, description="Ação recomendada para a equipe")

    model_config = ConfigDict(use_enum_values=True)
