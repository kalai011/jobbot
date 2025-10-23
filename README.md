# Job Auto-Apply Bot (Personal)

Personal Telegram bot that fetches job listings, notifies you, and safely autofills application forms (stopping before final submit).

**Warning:** Do NOT commit `.env` or any credentials.

## Quick start (local)
1. Copy `.env.example` to `.env` and fill credentials.
2. Put your resume in `resume_files/resume.pdf`.
3. Install deps:



python -m pip install -r requirements.txt
4. Run:

python bot.py

## Deploy to Railway
- Create a project, add Postgres plugin.
- Set environment variables in Railway: `TELEGRAM_TOKEN`, `DATABASE_URL`, `OPENAI_API_KEY`.
- Connect to GitHub and deploy.

## Notes
- Start with one platform scraper (e.g., Naukri/Indeed). Avoid aggressive scraping.
- For Selenium in cloud, use undetected-chromedriver or Playwright and test locally first.

