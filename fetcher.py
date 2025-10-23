# fetcher.py
import requests
from bs4 import BeautifulSoup
from db import SessionLocal, jobs
import datetime
import urllib.parse

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}

def fetch_indeed(query, location, max_results=10):
    q = urllib.parse.quote_plus(query)
    l = urllib.parse.quote_plus(location)
    url = f"https://in.indeed.com/jobs?q={q}&l={l}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    # This selector may change — keep it simple
    for card in soup.select("a[href*='/rc/clk']")[:max_results]:
        title = card.get_text(strip=True)
        href = card.get("href")
        if not href:
            continue
        link = urllib.parse.urljoin("https://in.indeed.com", href)
        job_id = link.split("/")[-1]
        results.append({
            "platform": "indeed",
            "job_id": job_id,
            "title": title,
            "company": "Unknown",
            "location": location,
            "link": link,
            "raw_html": str(card),
            "posted_at": datetime.datetime.now()
        })
    return results

def save_jobs(list_jobs):
    sess = SessionLocal()
    for j in list_jobs:
        try:
            insert = jobs.insert().values(
                platform=j["platform"],
                job_id=j["job_id"],
                title=j["title"],
                company=j.get("company"),
                location=j.get("location"),
                link=j["link"],
                raw_html=j.get("raw_html"),
                posted_at=j.get("posted_at")
            ).prefix_with("OR IGNORE")  # Works in some DBs; conflicts handled by unique constraint
            sess.execute(insert)
        except Exception as e:
            # simple upsert fallback
            try:
                sess.execute(
                    jobs.insert().values(
                        platform=j["platform"], job_id=j["job_id"],
                        title=j["title"], company=j.get("company"),
                        location=j.get("location"), link=j["link"],
                        raw_html=j.get("raw_html"), posted_at=j.get("posted_at")
                    )
                )
            except Exception as e2:
                print("Save job error:", e2)
    sess.commit()
    sess.close()

def run_job_fetch(queries=None):
    if queries is None:
        queries = [("Python Developer", "Coimbatore")]
    alljobs = []
    for q, loc in queries:
        alljobs.extend(fetch_indeed(q, loc))
        # add other platform fetchers later (naukri, linkedin public search)
    save_jobs(alljobs)
    return len(alljobs)

if __name__ == "__main__":
    init_count = run_job_fetch()
    print("Fetched jobs:", init_count)
