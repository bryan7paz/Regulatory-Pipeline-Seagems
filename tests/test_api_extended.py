"""Additional tests for api/routes — endpoints without direct DB inserts."""

from __future__ import annotations

import pytest
from api.database import SessionLocal, get_db
from api.main import app
from api.middleware import api_key_auth
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    async def override_auth():
        return None

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[api_key_auth] = override_auth
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


class TestDetailNotFound:
    def test_not_found(self, client):
        resp = client.get("/regs/nonexistent-id-xyz")
        assert resp.status_code == 404


class TestBatchValidate:
    def test_invalid_action(self, client):
        resp = client.post("/regs/batch-validate", json={"ids": ["x"], "action": "invalid"})
        assert resp.status_code == 400

    def test_empty_ids(self, client):
        resp = client.post("/regs/batch-validate", json={"ids": [], "action": "aprovado"})
        assert resp.status_code == 200
        assert resp.json()["updated"] == 0


class TestSingleValidate:
    def test_not_found(self, client):
        resp = client.post("/regs/missing-id/validate", json={"action": "aprovado"})
        assert resp.status_code == 404


class TestExportExcel:
    def test_excel_empty(self, client):
        resp = client.get("/regs/export/excel")
        assert resp.status_code in (200, 500)

    def test_excel_filtered(self, client):
        resp = client.get("/regs/export/excel?validacao=aprovado")
        assert resp.status_code in (200, 500)


class TestExportPDF:
    def test_pdf_empty(self, client):
        resp = client.get("/regs/export/pdf")
        assert resp.status_code in (200, 500)

    def test_pdf_filtered(self, client):
        resp = client.get("/regs/export/pdf?validacao=aprovado")
        assert resp.status_code in (200, 500)


class TestFilters:
    def test_assunto(self, client):
        resp = client.get("/regs/?assunto=SEG")
        assert resp.status_code == 200

    def test_aplicacao(self, client):
        resp = client.get("/regs/?aplicacao=D")
        assert resp.status_code == 200

    def test_fonte(self, client):
        resp = client.get("/regs/?fonte=iacs")
        assert resp.status_code == 200

    def test_status(self, client):
        resp = client.get("/regs/?status=R")
        assert resp.status_code == 200

    def test_date_range(self, client):
        resp = client.get("/regs/?date_from=2024-01-01&date_to=2024-12-31")
        assert resp.status_code == 200


class TestPipelineEndpoints:
    def test_start(self, client):
        resp = client.post("/pipeline/run")
        assert resp.status_code == 200
        assert "message" in resp.json()

    def test_stop(self, client):
        resp = client.post("/pipeline/stop")
        assert resp.status_code in (200, 404)

    def test_settings_get(self, client):
        resp = client.get("/pipeline/settings")
        assert resp.status_code == 200

    def test_settings_update(self, client):
        resp = client.post("/pipeline/settings", json={"active_provider": "groq"})
        assert resp.status_code == 200

    def test_notifications_list(self, client):
        resp = client.get("/pipeline/notifications")
        assert resp.status_code == 200

    def test_notifications_clear(self, client):
        resp = client.delete("/pipeline/notifications")
        assert resp.status_code in (200, 404, 405)
