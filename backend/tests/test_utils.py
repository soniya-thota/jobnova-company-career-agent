from app.providers import provider_career_root
from app.utils import detect_provider, valid_linkedin_job_url

def test_provider_detection():
    assert detect_provider("https://boards.greenhouse.io/acme/jobs/123") == "greenhouse"
    assert detect_provider("https://usource.ripplehire.com/candidate/?token=x") == "ripplehire"
    assert detect_provider("https://ibegin.tcsapps.com/candidate/jobs/417837J") == "tcs_ibegin"

def test_roots():
    assert provider_career_root("https://www.amazon.jobs/en/jobs/123/example") == "https://www.amazon.jobs/en"
    assert provider_career_root("https://ibegin.tcsapps.com/candidate/jobs/417837J") == "https://ibegin.tcsapps.com/candidate"

def test_linkedin_validation():
    assert valid_linkedin_job_url("https://www.linkedin.com/jobs/view/4437649151")
    assert not valid_linkedin_job_url("https://example.com/jobs/1")
