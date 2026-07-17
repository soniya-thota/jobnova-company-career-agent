# Jobnova Company Career Agent

A browser automation tool that discovers a company's official careers page from a LinkedIn job posting.

The application extracts company information from a LinkedIn job URL, follows the application flow, identifies the recruitment platform, and locates the corresponding careers page and matching job opening. It is built with FastAPI, Playwright, and a lightweight JavaScript frontend.

## Features

- Extract company information from LinkedIn job URLs
- Detect common Applicant Tracking Systems (ATS)
  - Workday
  - Greenhouse
  - Lever
  - Ashby
  - RippleHire
  - TCS iBegin
  - Google Careers
  - Amazon Jobs
- Discover the official company website
- Locate the company's careers page
- Find the matching job opening when available
- Return structured JSON results
- Optional browser automation mode for debugging

---

## Demo Workflow

```
LinkedIn Job URL
        │
        ▼
Extract Company Information
        │
        ▼
Detect ATS / Career Platform
        │
        ▼
Find Official Company Website
        │
        ▼
Locate Careers Page
        │
        ▼
Find Matching Job Opening
        │
        ▼
Return Structured Results
```

---

## Tech Stack

### Backend

- Python 3
- FastAPI
- Playwright
- Uvicorn

### Frontend

- HTML
- CSS
- JavaScript

### Development

- Docker
- Docker Compose
- Git

---

## Project Structure

```
jobnova-company-career-agent/
│
├── backend/
│   ├── app/
│   │   ├── agent.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── providers.py
│   │   └── utils.py
│   │
│   ├── tests/
│   ├── login.py
│   ├── run_windows.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── Dockerfile
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## Installation

Clone the repository.

```bash
git clone https://github.com/soniya-thota/jobnova-company-career-agent.git

cd jobnova-company-career-agent
```

Create a virtual environment.

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt

playwright install chromium
```

---

## Running the Project

Start the backend.

```bash
python login.py
python run_windows.py
```

Open the application.

```
http://127.0.0.1:8000
```

---

## Example Request

Input:

```
https://www.linkedin.com/jobs/view/...
```

Example response:

```json
{
  "company_name": "Google",
  "company_website_url": "https://about.google/",
  "career_page_url": "https://www.google.com/about/careers/applications",
  "open_position_url": "https://www.google.com/about/careers/applications/jobs/results/...",
  "provider": "Google Careers",
  "status": "success"
}
```

---

## Design Decisions

The agent uses a multi-step discovery pipeline rather than relying on a single search result.

1. Extract metadata from the LinkedIn job page.
2. Follow the Apply link.
3. Detect the recruitment platform.
4. Identify the official company website.
5. Locate the careers page.
6. Search for the corresponding job posting.
7. Return structured results with discovered links.

This layered approach improves robustness across companies using different hiring platforms.

---

## Current Limitations

- Some companies require authentication before exposing job details.
- Certain ATS providers limit automated access.
- Dynamic websites may occasionally require retries.
- Browser automation is intended for local execution.

---

## Future Improvements

- Support additional ATS providers
- Better company name normalization
- Confidence scoring for discovered results
- Parallel search pipeline
- Improved matching accuracy
- Cloud deployment support

---

## Author

**Soniya Thota**

MS in Computer Science  
University at Buffalo

LinkedIn: https://www.linkedin.com/in/soniya-thota/

GitHub: https://github.com/soniya-thota

---

## About This Project

This project was developed as part of a software engineering internship technical assessment. It demonstrates browser automation, backend API development, and career-page discovery using Playwright and FastAPI.