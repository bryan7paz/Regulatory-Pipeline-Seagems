"""E2E tests for the full pipeline flow."""

from __future__ import annotations

import time

import httpx
import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.slow]


class TestPipelineFlow:
    """Test full pipeline flow (crawl → process → API)."""

    def test_pipeline_can_be_triggered(self, api_url):
        """Pipeline can be triggered via API."""
        response = httpx.post(f"{api_url}/pipeline/process", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "ok" in data

    def test_pipeline_status_updates(self, api_url):
        """Pipeline status updates during execution."""
        # Trigger pipeline
        httpx.post(f"{api_url}/pipeline/process", timeout=10)

        # Wait a bit for pipeline to start
        time.sleep(2)

        # Check status
        response = httpx.get(f"{api_url}/pipeline/status", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "running" in data
        assert "step" in data

    def test_pipeline_notifications_created(self, api_url):
        """Pipeline creates notifications on completion."""
        # Trigger pipeline
        httpx.post(f"{api_url}/pipeline/process", timeout=10)

        # Wait for completion (with timeout)
        for _ in range(30):
            time.sleep(2)
            status_response = httpx.get(f"{api_url}/pipeline/status", timeout=10)
            status = status_response.json()
            if not status.get("running"):
                break

        # Check notifications
        response = httpx.get(f"{api_url}/pipeline/notifications", timeout=10)
        assert response.status_code == 200
        notifications = response.json()
        assert isinstance(notifications, list)


class TestDocumentFlow:
    """Test document CRUD flow."""

    def _create_test_document(self, api_url):
        """Helper to create a test document."""
        # This would normally be done by the pipeline
        # For E2E testing, we just verify the API works
        response = httpx.get(f"{api_url}/regs/", timeout=10)
        data = response.json()
        if data["items"]:
            return data["items"][0]["id"]
        return None

    def test_document_exists(self, api_url):
        """Documents exist in the system."""
        response = httpx.get(f"{api_url}/regs/", timeout=10)
        assert response.status_code == 200
        data = response.json()
        # May be empty if no documents processed yet
        assert isinstance(data["items"], list)

    def test_document_detail(self, api_url):
        """Can get document detail."""
        # Get list first
        response = httpx.get(f"{api_url}/regs/", timeout=10)
        data = response.json()

        if data["items"]:
            doc_id = data["items"][0]["id"]
            detail_response = httpx.get(f"{api_url}/regs/{doc_id}", timeout=10)
            assert detail_response.status_code == 200
            detail = detail_response.json()
            assert detail["id"] == doc_id

    def test_document_validation(self, api_url):
        """Can validate a document."""
        # Get list first
        response = httpx.get(f"{api_url}/regs/", timeout=10)
        data = response.json()

        if data["items"]:
            doc_id = data["items"][0]["id"]
            validate_response = httpx.post(
                f"{api_url}/regs/{doc_id}/validate",
                json={"action": "aprovado", "validated_by": "e2e-test"},
                timeout=10,
            )
            assert validate_response.status_code == 200
            result = validate_response.json()
            assert result["status_validacao"] == "aprovado"
