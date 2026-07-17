from __future__ import annotations
import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

TRACKING_KEYS = {"trk", "trackingid", "refid", "ref", "source", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"}

PROVIDERS = {
    "greenhouse": ("greenhouse.io", "boards.greenhouse.io", "job-boards.greenhouse.io"),
    "ashby": ("ashbyhq.com",),
    "lever": ("lever.co",),
    "workday": ("myworkdayjobs.com", "workdayjobs.com"),
    "smartrecruiters": ("smartrecruiters.com",),
    "icims": ("icims.com",),
    "successfactors": ("successfactors.com",),
    "oracle": ("oraclecloud.com", "oracle.com"),
    "ripplehire": ("ripplehire.com",),
    "tcs_ibegin": ("ibegin.tcsapps.com",),
    "amazon_jobs": ("amazon.jobs",),
}

def clean_text(value: str | None) -> str | None:
    if not value:
        return None
    value = re.sub(r"\s+", " ", value).strip()
    return value or None

def host(url: str | None) -> str:
    if not url:
        return ""
    return urlparse(url).netloc.lower().removeprefix("www.")

def detect_provider(url: str | None) -> str:
    domain = host(url)
    for name, domains in PROVIDERS.items():
        if any(domain == d or domain.endswith("." + d) for d in domains):
            return name
    return "generic"

def strip_tracking(url: str) -> str:
    parsed = urlparse(url)
    query = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if k.lower() not in TRACKING_KEYS]
    return urlunparse(parsed._replace(query=urlencode(query), fragment=""))

def valid_linkedin_job_url(url: str) -> bool:
    p = urlparse(url)
    return p.scheme in {"http", "https"} and (p.netloc.endswith("linkedin.com") or p.netloc.endswith("www.linkedin.com")) and "/jobs/view/" in p.path

def infer_company_from_host(url: str | None) -> str | None:
    domain = host(url)
    known = {
        "amazon.jobs": "Amazon",
        "ibegin.tcsapps.com": "Tata Consultancy Services",
        "usource.ripplehire.com": "UST",
    }
    if domain in known:
        return known[domain]
    parts = domain.split(".")
    if not parts:
        return None
    token = parts[-2] if len(parts) >= 2 else parts[0]
    if token in {"greenhouse", "ashbyhq", "lever", "workdayjobs", "smartrecruiters", "icims", "ripplehire", "tcsapps"}:
        return None
    return token.replace("-", " ").title()
