import random
from .models import Observation, Action, Reward, EmailAnalysis
from .data import EMAIL_DATA
from .grader import detect_category, extract_main_subject

class EmailEnv:
    def __init__(self, task="easy"):
        self.task = task
        self.reset()

    def reset(self):
        self.step_count = 0
        self.current_email = random.choice(EMAIL_DATA[self.task])
        return Observation(email=self.current_email, step_count=0)

    def step(self, action: Action):
        self.step_count += 1

        detected_category, confidence, reason = detect_category(
            f"Subject: {self.current_email.subject}\n\n{self.current_email.body}"
        )
        score = 1.0 if action.label == detected_category else 0.0
        reason = f"{reason} Predicted: {action.label}, detected: {detected_category}."

        done = True

        return (
            Observation(email=self.current_email, step_count=self.step_count),
            Reward(score=score, reason=reason),
            done,
            {}
        )

    def state(self):
        return {
            "email": self.current_email.dict(),
            "step_count": self.step_count
        }

    def analyze_text(self, raw_text: str) -> EmailAnalysis:
        category, confidence, reason = detect_category(raw_text)
        main_subject = extract_main_subject(raw_text)
        return EmailAnalysis(
            category=category,
            main_subject=main_subject,
            confidence=confidence,
            reason=reason,
        )