"""Tests for core/config.py."""
from __future__ import annotations

from core.config import load_sources, load_prompt, validate_env


class TestLoadSources:
    def test_returns_list(self):
        sources = load_sources()
        assert isinstance(sources, list)

    def test_has_ids(self):
        sources = load_sources()
        ids = {s["id"] for s in sources}
        assert "panama" in ids
        assert "imodocs" in ids

    def test_imodocs_has_auth(self):
        sources = load_sources()
        imodocs = next(s for s in sources if s["id"] == "imodocs")
        assert "auth" in imodocs
        assert imodocs["type"] == "login"


class TestLoadPrompt:
    def test_returns_dict(self):
        prompt = load_prompt()
        assert isinstance(prompt, dict)

    def test_has_required_keys(self):
        prompt = load_prompt()
        for key in ("system", "contexto_empresa", "instrucoes",
                     "legenda_assunto", "legenda_aplicacao", "legenda_status",
                     "regras_duras"):
            assert key in prompt, f"Missing key: {key}"


class TestValidateEnv:
    def test_missing_vars(self):
        missing = validate_env({})
        assert "GOOGLE_API_KEY" in missing
        assert "DATABASE_URL" in missing

    def test_all_set(self):
        env = {"GOOGLE_API_KEY": "real-key", "DATABASE_URL": "pg://..."}
        assert validate_env(env) == []

    def test_placeholder_rejected(self):
        env = {"GOOGLE_API_KEY": "your_key_here", "DATABASE_URL": "pg://..."}
        missing = validate_env(env)
        assert "GOOGLE_API_KEY" in missing