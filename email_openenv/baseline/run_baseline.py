import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from env.environment import EmailEnv
from env.data import EMAIL_DATA

env = EmailEnv("easy")

for task in ["easy", "medium", "hard"]:
    print(f"\nTask: {task}")
    for email in EMAIL_DATA[task]:
        raw = f"Subject: {email.subject}\n\n{email.body}"
        result = env.analyze_text(raw)
        print(f"- Subject: {email.subject}")
        print(f"  Category: {result.category}")
        print(f"  Main Subject: {result.main_subject}")
        print(f"  Confidence: {int(result.confidence * 100)}%")
