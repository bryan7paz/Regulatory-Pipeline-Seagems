"""Pydantic schema for the structured regulatory analysis.

Mirrors the spreadsheet columns:

    Data Publicacao | Entrada Em Vigor | Requisito | Norma | Assunto |
    Aplicacao | Status | Item | Itens Modificados / Objetivos | Acao Sugerida
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

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

    data_publicacao: Optional[str] = Field(
        None, description="Data de elaboração/publicação no formato AAAA-MM-DD"
    )
    entrada_em_vigor: Optional[str] = Field(
        None, description="Data de entrada em vigor no formato AAAA-MM-DD"
    )
    requisito: Optional[str] = Field(None, description="Autoridade/fonte emissora")
    norma: Optional[str] = Field(None, description="Código + título da norma")
    assunto: Optional[Assunto] = Field(None, description="Categoria do assunto (sigla)")
    aplicacao: Optional[Aplicacao] = Field(
        None, description="D (direta), I (indireta) ou NP (não pertinente)"
    )
    status: Optional[Status] = Field(None, description="R (revisão) ou N (nova versão)")
    item: Optional[str] = Field(None, description="Item/trecho específico alterado")
    itens_modificados: Optional[str] = Field(None, description="Descrição do que mudou")
    acao_sugerida: Optional[str] = Field(None, description="Ação recomendada para a equipe")

    model_config = ConfigDict(use_enum_values=True)