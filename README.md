# Jobnova Company Career Agent v3

A FastAPI + Playwright agent for Part 2 of the Jobnova AI Engineer take-home challenge. It accepts a LinkedIn job URL, captures the external Apply destination, classifies the hiring provider, derives the careers portal, and returns one opening URL.

## Output

- Company name
- Official company website when it can be verified
- Careers page URL
- Opening URL
- Provider, confidence, discovery time, and warnings

## Windows setup

```bat
cd jobnova-company-career-agent-v3\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python login.py
python run_windows.py
```

Open `http://127.0.0.1:8000`.

The **Watch browser automation** checkbox is empty by default. Leave it unchecked for headless operation; check it only when you want to watch the browser.

## API

`POST /api/v1/discover`

```json
{
  "linkedin_url": "https://www.linkedin.com/jobs/view/4437649151",
  "show_browser": false
}
```

Health check: `GET /api/v1/health`

## Tests

```bat
cd backend
pytest
```

## Docker

```bash
docker compose up --build
```

Headed browser mode is intended for local execution; Docker should normally use `show_browser: false`.

## Supported provider classification

Greenhouse, Ashby, Lever, Workday, SmartRecruiters, iCIMS, SuccessFactors, Oracle, RippleHire, TCS iBegin, Amazon Jobs, and generic career portals.

## Known limitations

LinkedIn may change its markup, require authentication, rate-limit requests, or remove expired jobs. Some ATS pages do not expose an official corporate website. In those cases, the agent returns the verified external role and a derived careers portal with an explicit warning rather than inventing data.
