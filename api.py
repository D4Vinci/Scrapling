from fastapi import FastAPI, Query
from scrapling.fetchers import StealthyFetcher
import uvicorn

app = FastAPI(title="LinkedIn Job Scraper API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/scrape/linkedin")
def scrape_linkedin(
    keywords: str = Query(..., description="Job title to search"),
    location: str = Query(default="India"),
):
    url = (
        f"https://www.linkedin.com/jobs/search/"
        f"?keywords={keywords.replace(' ', '%20')}"
        f"&location={location.replace(' ', '%20')}"
        f"&f_TPR=r86400&f_AL=true&distance=25"
    )

    try:
        page = StealthyFetcher.fetch(
            url,
            headless=True,
            network_idle=True,
            disable_resources=True
        )

        jobs = []

        # Try multiple LinkedIn card selectors — they change layout sometimes
        cards = (
            page.css('.base-card') or
            page.css('.job-search-card') or
            page.css('[data-entity-urn]') or
            []
        )

        for card in cards:
            title_el   = (card.css('.base-search-card__title') or card.css('h3')).first
            company_el = (card.css('.base-search-card__subtitle') or card.css('h4')).first
            loc_el     = (card.css('.job-search-card__location') or card.css('.base-search-card__metadata')).first
            link_el    = card.css('a').first
            date_el    = card.css('time').first

            title   = title_el.text.strip()   if title_el   else ''
            company = company_el.text.strip()  if company_el else ''
            loc     = loc_el.text.strip()      if loc_el     else ''
            link    = link_el.attrib.get('href', '') if link_el else ''
            date    = date_el.attrib.get('datetime', '') if date_el else ''

            # Extract numeric job ID from URL
            import re
            id_match = re.search(r'(\d{8,})', link)
            job_id   = id_match.group(1) if id_match else link[-16:]

            if title:
                jobs.append({
                    "jobId":       job_id,
                    "jobTitle":    title,
                    "company":     company,
                    "location":    loc,
                    "rawLink":     link.split('?')[0] if link else '',
                    "description": "",
                    "pubDate":     date,
                })

        return {"success": True, "count": len(jobs), "jobs": jobs}

    except Exception as e:
        return {"success": False, "error": str(e), "jobs": []}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
