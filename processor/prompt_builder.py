"""Prompt builder: assembles the full prompt from config/prompt.yaml."""
from __future__ import annotations

from core.config import load_prompt


def build_prompt(document_text: str) -> tuple[str, str]:
    """Compose the system + instructions + document for the LLM.

    Returns:
        (system_prompt, user_prompt) tuple.
    """
    cfg = load_prompt()

    system = cfg.get("system", "")
    contexto = cfg.get("contexto_empresa", "")
    instrucoes = cfg.get("instrucoes", "")
    legenda_assunto = cfg.get("legenda_assunto", "")
    legenda_aplicacao = cfg.get("legenda_aplicacao", {})
    legenda_status = cfg.get("legenda_status", {})
    regras = cfg.get("regras_duras", "")

    legenda_aplicacao_text = "\n".join(f"  {k}: {v}" for k, v in legenda_aplicacao.items())
    legenda_status_text = "\n".join(f"  {k}: {v}" for k, v in legenda_status.items())

    system_prompt = (
        f"{system}\n\n"
        f"{contexto}\n\n"
        f"{instrucoes}\n\n"
        f"Legenda de Assunto:\n{legenda_assunto}\n\n"
        f"Legenda de Aplicação:\n{legenda_aplicacao_text}\n\n"
        f"Legenda de Status:\n{legenda_status_text}\n\n"
        f"{regras}"
    )

    user_prompt = f"Documento a analisar:\n\n{document_text}"

    return system_prompt, user_prompt