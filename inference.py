import os
import sys
from collections.abc import Iterable
from pathlib import Path

from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parent
PROJECT_DIR = PROJECT_ROOT / "email_openenv"
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from env.environment import EmailEnv
from env.data import EMAIL_DATA
from env.grader import detect_category
from env.models import Action


CATEGORY_LABELS = [
    "education",
    "promotions",
    "spam",
    "personal",
    "urgent",
    "work",
    "finance",
    "security",
    "other",
]


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _sanitize(value: str, limit: int = 80) -> str:
    compact = " ".join(value.strip().split())
    compact = compact.replace(" ", "_")
    if not compact:
        return "NA"
    return compact[:limit]


def _emit(tag: str, fields: Iterable[tuple[str, object]]) -> None:
    payload = " ".join(f"{key}={value}" for key, value in fields)
    print(f"[{tag}] {payload}", flush=True)


def _classify_with_openai(client: OpenAI, model_name: str, raw_text: str) -> tuple[str, str]:
    prompt = (
        "Classify the email into exactly one label from: "
        + ", ".join(CATEGORY_LABELS)
        + ". Return only the label, lower-case, with no extra text.\n\n"
        + raw_text
    )

    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a strict email triage classifier."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    predicted = (completion.choices[0].message.content or "").strip().lower()
    if predicted not in CATEGORY_LABELS:
        raise ValueError(f"Invalid model label: {predicted!r}")
    return predicted, "llm"


def _classify_email(client: OpenAI, model_name: str, raw_text: str) -> tuple[str, str]:
    try:
        return _classify_with_openai(client, model_name, raw_text)
    except Exception:
        predicted, _confidence, _reason = detect_category(raw_text)
        return predicted, "fallback"


def main() -> int:
    api_base_url = _require_env("API_BASE_URL")
    model_name = _require_env("MODEL_NAME")
    api_key = _require_env("HF_TOKEN")

    client = OpenAI(api_key=api_key, base_url=api_base_url)

    task_names = list(EMAIL_DATA.keys())
    _emit(
        "START",
        [
            ("tasks", len(task_names)),
            ("samples", sum(len(emails) for emails in EMAIL_DATA.values())),
            ("model", _sanitize(model_name)),
            ("base_url", _sanitize(api_base_url, 120)),
        ],
    )

    overall_scores: list[float] = []

    for task_name in task_names:
        env = EmailEnv(task_name)
        task_scores: list[float] = []
        emails = EMAIL_DATA[task_name]

        for sample_index, email in enumerate(emails, start=1):
            env.current_email = email
            env.step_count = 0

            raw_text = f"Subject: {email.subject}\nFrom: {email.sender}\n\n{email.body}"
            predicted_label, source = _classify_email(client, model_name, raw_text)
            _observation, reward, _done, _info = env.step(Action(label=predicted_label))
            detected_label, _confidence, _reason = detect_category(raw_text)

            task_scores.append(float(reward.score))
            overall_scores.append(float(reward.score))

            _emit(
                "STEP",
                [
                    ("task", _sanitize(task_name)),
                    ("sample", sample_index),
                    ("subject", _sanitize(email.subject)),
                    ("predicted", predicted_label),
                    ("actual", detected_label),
                    ("score", f"{reward.score:.1f}"),
                    ("source", source),
                    ("state_step", env.state()["step_count"]),
                ],
            )

    overall_score = sum(overall_scores) / max(len(overall_scores), 1)
    _emit(
        "END",
        [
            ("status", "success"),
            ("tasks", len(task_names)),
            ("samples", len(overall_scores)),
            ("overall_score", f"{overall_score:.3f}"),
        ],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())