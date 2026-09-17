"""Tests for processor/normalizer.py."""

from __future__ import annotations

from processor.normalizer import normalize


class TestNormalize:
    def test_valid_full(self):
        raw = {
            "norma": "MMC-169",
            "assunto": "COM",
            "aplicacao": "D",
            "status": "R",
        }
        r = normalize(raw)
        assert r.norma == "MMC-169"
        assert r.assunto == "COM"
        assert r.aplicacao == "D"
        assert r.status == "R"

    def test_invalid_assunto_drops_all_enums(self):
        raw = {"norma": "X", "assunto": "INVALIDO", "aplicacao": "D", "status": "R"}
        r = normalize(raw)
        # normalizer drops ALL enum fields when any is invalid
        assert r.assunto is None
        assert r.aplicacao is None

    def test_invalid_aplicacao_dropped(self):
        raw = {"norma": "X", "assunto": "SEG", "aplicacao": "ZZZ"}
        r = normalize(raw)
        assert r.aplicacao is None
        assert r.assunto is None  # enum fields dropped together

    def test_empty_dict(self):
        r = normalize({})
        assert r.norma is None
        assert r.aplicacao is None

    def test_np_preserved(self):
        raw = {"aplicacao": "NP", "assunto": "CON"}
        r = normalize(raw)
        assert r.aplicacao == "NP"
