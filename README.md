---
title: Email Smart Triage
emoji: "📧"
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
pinned: false
---

# Email Smart Triage

Automatic email triage app built with Streamlit.

## Submission Requirements

The inference entrypoint is [inference.py](inference.py) and it expects these environment variables to be defined before running:

- `API_BASE_URL`
- `MODEL_NAME`
- `HF_TOKEN`

The script uses the OpenAI client for model calls and emits structured `[START]`, `[STEP]`, and `[END]` logs.

It detects:
- Category: education, promotions, spam, personal, urgent, work, finance, security, or other
- Main subject: short topic summary for quick scanning

## Local Run

From repository root:

streamlit run app.py

## Project Source

Core project files are in the email_openenv folder.