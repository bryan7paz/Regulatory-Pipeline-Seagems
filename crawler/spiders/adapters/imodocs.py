"""IMODOCS adapter — authenticated spider for IMO documents portal."""

from __future__ import annotations

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from core.config import load_env, logger

from crawler.spiders.base import BaseSpider, Item


class ImodocsAdapter(BaseSpider):
    """IMODOCS-specific spider with login, pagination, and date extraction."""

    BASE_URL = "https://docs.imo.org"

    async def fetch_items(self) -> list[Item]:
        from core.browser import get_browser

        env = load_env()
        auth = self.source.get("auth", {})
        user = env.get(auth.get("user_env", "IMODOCS_USER"), "")
        password = env.get(auth.get("password_env", "IMODOCS_PASSWORD"), "")

        if not user or not password:
            raise RuntimeError(
                "Credenciais IMODOCS não configuradas. "
                "Defina IMODOCS_USER e IMODOCS_PASSWORD em config/secrets.env"
            )

        login_url = auth.get("login_url", f"{self.BASE_URL}/en/LogOn")
        username_sel = auth.get("username_selector", "#Username")
        password_sel = auth.get("password_selector", "#Password")
        submit_sel = auth.get("submit_selector", "input[type=submit], button[type=submit]")

        all_items: list[Item] = []

        async with get_browser() as page:
            # Login
            logger.info("Fazendo login no IMODOCS...")
            await page.goto(login_url, wait_until="domcontentloaded", timeout=60000)

            try:
                await page.fill(username_sel, user, timeout=15000)
                await page.fill(password_sel, password, timeout=10000)
                await page.click(submit_sel, timeout=10000)
                await page.wait_for_load_state("networkidle", timeout=30000)
            except Exception as exc:
                raise RuntimeError(f"Falha no login IMODOCS: {exc}") from exc

            logger.info("Login OK, buscando documentos...")

            # Navigate to document listing page
            search_url = auth.get("search_url", f"{self.BASE_URL}/en/Search")
            await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_load_state("networkidle", timeout=30000)

            # Extract items from current page
            html = await page.content()
            all_items.extend(self._extract_items(html))

            # Handle pagination (up to 5 pages max)
            max_pages = self.source.get("max_pages", 5)
            for page_num in range(2, max_pages + 1):
                try:
                    next_btn = await page.query_selector(
                        f'a:has-text("{page_num}"), .pagination a:text("{page_num}")'
                    )
                    if not next_btn:
                        break
                    await next_btn.click()
                    await page.wait_for_load_state("networkidle", timeout=20000)
                    html = await page.content()
                    items = self._extract_items(html)
                    if not items:
                        break
                    all_items.extend(items)
                except Exception:
                    break

        logger.info("IMODOCS: %d documentos encontrados", len(all_items))
        return all_items

    def _extract_items(self, html: str) -> list[Item]:
        """Extract document links and metadata from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        items: list[Item] = []
        seen: set[str] = set()

        # IMODOCS uses table rows or card layouts for document listings
        for row in soup.select("tr, .document-row, .search-result"):
            links = row.find_all("a", href=True)
            for a in links:
                href = a["href"]
                if not href or href == "#":
                    continue

                # Must link to a document (PDF, HTML, or detail page)
                if not any(
                    ext in href.lower() for ext in [".pdf", "/document/", "/detail", "/view"]
                ):
                    continue

                title = a.get_text(" ", strip=True)
                if not title or len(title) < 3:
                    # Try to get title from row context
                    title = row.get_text(" ", strip=True)[:200] or "Documento IMO"

                full_url = urljoin(self.BASE_URL, href)
                if full_url in seen:
                    continue
                seen.add(full_url)

                # Try to extract date from row context
                date = self._extract_date(row)

                items.append(
                    Item(
                        title=title,
                        url=full_url,
                        published_date=date,
                        source_id=self.source_id,
                        extra={"portal": "imodocs"},
                    )
                )

        # Fallback: extract all PDF links if no structured listing found
        if not items:
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.lower().endswith(".pdf"):
                    full_url = urljoin(self.BASE_URL, href)
                    if full_url not in seen:
                        seen.add(full_url)
                        title = a.get_text(" ", strip=True) or "Documento IMO"
                        items.append(
                            Item(
                                title=title,
                                url=full_url,
                                source_id=self.source_id,
                                extra={"portal": "imodocs"},
                            )
                        )

        return items

    def _extract_date(self, element) -> str | None:
        """Try to extract a date from the HTML element."""
        text = element.get_text(" ", strip=True)
        # Match common date formats
        patterns = [
            r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})",  # DD/MM/YYYY
            r"(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})",  # YYYY-MM-DD
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                groups = m.groups()
                if len(groups[0]) == 4:
                    return f"{groups[0]}-{groups[1].zfill(2)}-{groups[2].zfill(2)}"
                return f"{groups[2]}-{groups[1].zfill(2)}-{groups[0].zfill(2)}"
        return None
