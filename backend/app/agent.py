from __future__ import annotations
import asyncio, json, re, time
from contextlib import suppress
from typing import Any
from urllib.parse import urljoin, urlparse
from playwright.async_api import Page, async_playwright
from .models import DiscoverResult
from .providers import provider_career_root
from .utils import clean_text, detect_provider, host, infer_company_from_host, strip_tracking, valid_linkedin_job_url

TITLE_SELECTORS = ("h1.top-card-layout__title", ".job-details-jobs-unified-top-card__job-title h1", ".jobs-unified-top-card__job-title h1", "main h1")
COMPANY_SELECTORS = (".job-details-jobs-unified-top-card__company-name a", ".jobs-unified-top-card__company-name a", ".topcard__org-name-link")
LOCATION_SELECTORS = (".job-details-jobs-unified-top-card__primary-description-container", ".jobs-unified-top-card__bullet", ".topcard__flavor--bullet")
APPLY_SELECTORS = ("button.jobs-apply-button", "button[aria-label*='Apply']", "a[aria-label*='Apply']", "button:has-text('Apply')", "a:has-text('Apply')")

async def first_text(page: Page, selectors: tuple[str, ...]) -> str | None:
    for s in selectors:
        try:
            loc = page.locator(s).first
            if await loc.count() and await loc.is_visible():
                text = clean_text(await loc.inner_text())
                if text: return text
        except Exception:
            pass
    return None

async def meta(page: Page, key: str, attr: str = "property") -> str | None:
    try:
        return clean_text(await page.locator(f'meta[{attr}="{key}"]').first.get_attribute("content"))
    except Exception:
        return None

async def jsonld_metadata(page: Page) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    scripts = page.locator("script[type='application/ld+json']")
    for i in range(await scripts.count()):
        raw = await scripts.nth(i).text_content()
        if not raw: continue
        with suppress(Exception):
            parsed = json.loads(raw)
            queue: list[Any] = parsed if isinstance(parsed, list) else [parsed]
            while queue:
                item = queue.pop(0)
                if isinstance(item, dict):
                    if item.get("@type") == "JobPosting":
                        out["title"] = clean_text(item.get("title"))
                        org = item.get("hiringOrganization")
                        if isinstance(org, dict): out["company"] = clean_text(org.get("name"))
                        return out
                    queue.extend(v for v in item.values() if isinstance(v, (dict, list)))
                elif isinstance(item, list): queue.extend(item)
    return out

async def capture_apply(page: Page) -> tuple[str | None, str | None]:
    for s in APPLY_SELECTORS:
        loc = page.locator(s)
        for i in range(min(await loc.count(), 8)):
            btn = loc.nth(i)
            try:
                if not await btn.is_visible(): continue
                label = clean_text((await btn.inner_text()) or (await btn.get_attribute("aria-label"))) or ""
                if "easy apply" in label.lower(): return page.url, "linkedin_easy_apply"
                href = await btn.get_attribute("href")
                if href and "linkedin.com" not in host(urljoin(page.url, href)):
                    return strip_tracking(urljoin(page.url, href)), "href"
                before = set(p.url for p in page.context.pages)
                async with page.expect_popup(timeout=5000) as popup_info:
                    await btn.click()
                popup = await popup_info.value
                await popup.wait_for_load_state("domcontentloaded", timeout=15000)
                return strip_tracking(popup.url), "popup"
            except Exception:
                with suppress(Exception):
                    await btn.click(timeout=5000)
                    await page.wait_for_timeout(2500)
                    if "linkedin.com" not in host(page.url): return strip_tracking(page.url), "same_tab"
    return None, None

async def discover(linkedin_url: str, show_browser: bool = False) -> DiscoverResult:
    started = time.perf_counter()
    if not valid_linkedin_job_url(linkedin_url):
        return DiscoverResult(status="invalid_url", warnings=["Enter a LinkedIn job URL in the form https://www.linkedin.com/jobs/view/..."])
    warnings: list[str] = []
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=".jobnova_browser_profile", headless=not show_browser,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            viewport=None if show_browser else {"width": 1440, "height": 1000},
        )
        page = context.pages[0] if context.pages else await context.new_page()
        page.set_default_timeout(12000)
        page.set_default_navigation_timeout(30000)
        try:
            await page.goto(linkedin_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(1800)
            ld = await jsonld_metadata(page)
            title = ld.get("title") or await first_text(page, TITLE_SELECTORS)
            company = ld.get("company") or await first_text(page, COMPANY_SELECTORS)
            location = await first_text(page, LOCATION_SELECTORS)
            if not title:
                og = await meta(page, "og:title") or await meta(page, "twitter:title", "name")
                if og and " | " in og: title = clean_text(og.split(" | ", 1)[0])
            apply_url, method = await capture_apply(page)
            if not apply_url:
                return DiscoverResult(status="apply_url_not_found", company_name=company, linkedin_job_title=title,
                    linkedin_location=location, warnings=["A visible external Apply destination could not be captured."],
                    discovery_time_seconds=round(time.perf_counter()-started, 2))
            if method == "linkedin_easy_apply":
                return DiscoverResult(status="linkedin_easy_apply", company_name=company, linkedin_job_title=title,
                    linkedin_location=location, captured_apply_url=apply_url, provider="linkedin", open_position_url=apply_url,
                    role_match_method="linkedin_easy_apply", confidence=100,
                    discovery_time_seconds=round(time.perf_counter()-started, 2),
                    warnings=["This listing uses LinkedIn Easy Apply and does not expose an external careers URL."])

            provider = detect_provider(apply_url)
            career = provider_career_root(apply_url)
            company = company or infer_company_from_host(apply_url)
            website = None
            # Verify an official corporate link from the external page where practical.
            ext = await context.new_page()
            with suppress(Exception):
                await ext.goto(apply_url, wait_until="domcontentloaded", timeout=30000)
                await ext.wait_for_timeout(1000)
                if not company:
                    company = (await jsonld_metadata(ext)).get("company") or await first_text(ext, ("[data-qa='company-name']", ".company-name", "header img[alt]"))
                links = ext.locator("a[href^='http']")
                ats_host = host(apply_url)
                for i in range(min(await links.count(), 120)):
                    href = await links.nth(i).get_attribute("href")
                    if not href: continue
                    h = host(href)
                    text = (clean_text(await links.nth(i).inner_text()) or "").lower()
                    if h and h != ats_host and not any(x in h for x in ("linkedin.com","facebook.com","twitter.com","instagram.com","youtube.com")):
                        if any(k in text for k in ("company website", "visit website", "about us", "homepage")):
                            website = strip_tracking(href); break
            if not website:
                warnings.append("The official corporate website was not reliably found; the careers portal derived from the external job URL is used.")
            if not title:
                warnings.append("LinkedIn job title could not be extracted, so the captured external role was returned without claiming an exact title match.")
            confidence = 95
            if not company: confidence -= 15
            if not website: confidence -= 8
            if not title: confidence -= 7
            return DiscoverResult(status="success", company_name=company, company_website_url=website,
                career_page_url=career, open_position_url=apply_url, linkedin_job_title=title,
                linkedin_location=location, captured_apply_url=apply_url, provider=provider,
                role_match_method="captured_apply_url_fallback" if not title else "captured_external_role",
                confidence=max(confidence, 55), discovery_time_seconds=round(time.perf_counter()-started, 2), warnings=warnings)
        except Exception as exc:
            return DiscoverResult(status="error", warnings=[f"{type(exc).__name__}: {exc}"], discovery_time_seconds=round(time.perf_counter()-started, 2))
        finally:
            await context.close()
