# autofill.py
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from db import SessionLocal, jobs, applications
import tempfile

def get_job_link(job_db_id):
    sess = SessionLocal()
    row = sess.execute(jobs.select().where(jobs.c.id == job_db_id)).first()
    sess.close()
    return row.link if row else None

def autofill_job(job_db_id, user_profile):
    """
    Opens the job apply link, tries to fill common fields, saves screenshot and returns
    an object for the bot to send to user.
    This function DOES NOT press the final submit button.
    """
    url = get_job_link(job_db_id)
    if not url:
        return False, {"error": "Job link not found"}

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Options to avoid detection
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1200, 900)
    try:
        driver.get(url)
        time.sleep(3)
        # Example fillers — these are site-specific. Check the page and change selectors.
        try:
            # Common field names — won't work everywhere; used as template
            if user_profile.get("full_name"):
                elems = driver.find_elements(By.XPATH, "//input[contains(@name,'name') or contains(@id,'name') or contains(@placeholder,'Name')]")
                for e in elems:
                    try:
                        e.clear()
                        e.send_keys(user_profile["full_name"])
                    except:
                        pass
            if user_profile.get("email"):
                elems = driver.find_elements(By.XPATH, "//input[contains(@name,'email') or contains(@id,'email') or contains(@placeholder,'Email')]")
                for e in elems:
                    try:
                        e.clear()
                        e.send_keys(user_profile["email"])
                    except:
                        pass
            if user_profile.get("phone"):
                elems = driver.find_elements(By.XPATH, "//input[contains(@name,'phone') or contains(@id,'phone') or contains(@placeholder,'Phone')]")
                for e in elems:
                    try:
                        e.clear()
                        e.send_keys(user_profile["phone"])
                    except:
                        pass
        except Exception as ex:
            print("fill error", ex)

        # Save screenshot to temp file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        path = tmp.name
        driver.save_screenshot(path)

        # Log 'filled' application in DB (status = filled, semi-auto)
        sess = SessionLocal()
        sess.execute(applications.insert().values(
            user_id=1, job_db_id=job_db_id, status="filled", apply_mode="semi-auto"
        ))
        sess.commit()
        sess.close()

        driver.quit()
        return True, {"url": url, "screenshot_path": path}
    except Exception as e:
        driver.quit()
        return False, {"error": str(e)}
