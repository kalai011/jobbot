# ai_helpers.py
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_cover_letter(job_title, company_name, resume_bullets):
    prompt = f"Write a short (3-4 paragraph) professional cover letter for the role {job_title} at {company_name}. My resume bullets: {resume_bullets}"
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-5-mini",
            messages=[{"role":"user","content":prompt}],
            max_tokens=350,
            temperature=0.6
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("OpenAI error:", e)
        return "Sorry, could not generate cover letter right now."
