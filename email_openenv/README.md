# Smart Email Triage OpenEnv

## Description
Paste an email and the app automatically detects:
- Category: education, promotions, spam, personal, urgent, work, finance, security, or other
- Main subject: short summary/topic of the email

Users do not need to choose any label manually.

## How It Works
- Rule-based signal matching for category detection
- Subject extraction from `Subject:` line (if present)
- Fallback topic inference from body text

## Run UI
If you are inside the `email_openenv` folder:
streamlit run app.py

If you are at workspace root (`META_EMAIL`):
streamlit run email_openenv/app.py

## Run baseline script
python baseline/run_baseline.py