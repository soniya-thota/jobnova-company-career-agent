from __future__ import annotations
from urllib.parse import urlparse, urlunparse
from .utils import detect_provider

def provider_career_root(url: str) -> str | None:
    p = urlparse(url)
    provider = detect_provider(url)
    path = p.path or "/"
    if provider == "amazon_jobs":
        seg = [x for x in path.split("/") if x]
        lang = seg[0] if seg and len(seg[0]) <= 5 else "en"
        return urlunparse((p.scheme, p.netloc, f"/{lang}", "", "", ""))
    if provider == "tcs_ibegin":
        return urlunparse((p.scheme, p.netloc, "/candidate", "", "", ""))
    if provider == "ripplehire":
        # Tokens can be required to identify the tenant, so preserve the query.
        return urlunparse((p.scheme, p.netloc, "/candidate/", "", p.query, ""))
    if provider in {"greenhouse", "ashby", "lever", "smartrecruiters"}:
        seg = [x for x in path.split("/") if x]
        if seg:
            return urlunparse((p.scheme, p.netloc, "/" + seg[0], "", "", ""))
    if provider == "workday":
        seg = [x for x in path.split("/") if x]
        if len(seg) >= 2:
            return urlunparse((p.scheme, p.netloc, "/" + "/".join(seg[:2]), "", "", ""))
    # Generic: remove obvious job-detail suffix only when safe.
    lower = path.lower()
    for marker in ("/jobs/", "/job/", "/positions/", "/opening/"):
        if marker in lower:
            idx = lower.index(marker)
            root = path[:idx] or "/"
            return urlunparse((p.scheme, p.netloc, root.rstrip("/") or "/", "", "", ""))
    return urlunparse((p.scheme, p.netloc, path, "", p.query, ""))
