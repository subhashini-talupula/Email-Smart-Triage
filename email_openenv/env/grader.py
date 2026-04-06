import re
from collections import Counter


CATEGORY_KEYWORDS = {
    "education": [
        ("course", 1.2), ("learning", 1.1), ("academy", 1.3), ("training", 1.1),
        ("class", 1.0), ("exam", 1.1), ("assignment", 1.1), ("python essentials", 1.5),
        ("ideathon", 1.5), ("faculty", 1.2), ("university", 1.2), ("college", 1.2),
        ("student", 1.0), ("my learning", 1.2), ("certification", 1.1),
    ],
    "promotions": [
        ("offer", 1.2), ("discount", 1.3), ("deal", 1.2), ("sale", 1.2),
        ("coupon", 1.2), ("save", 1.0), ("limited time", 1.1), ("exclusive", 1.1),
        ("new arrivals", 1.0), ("shop now", 1.2), ("promo", 1.1),
    ],
    "spam": [
        ("free", 1.0), ("winner", 1.5), ("won", 1.4), ("prize", 1.5),
        ("lottery", 1.6), ("click", 0.8), ("buy now", 1.0), ("exclusive deal", 1.0),
        ("unsubscribe", 0.5), ("act now", 1.0), ("guaranteed", 1.2), ("risk free", 1.2),
        ("crypto", 1.2),
    ],
    "urgent": [
        ("urgent", 1.5), ("asap", 1.4), ("immediately", 1.4), ("today", 0.9), ("now", 0.7),
        ("critical", 1.5), ("important", 0.8), ("deadline", 1.1), ("action required", 1.5),
        ("escalation", 1.3), ("by eod", 1.2), ("before", 0.7),
    ],
    "work": [
        ("meeting", 1.2), ("project", 1.2), ("client", 1.0), ("team", 0.9), ("report", 1.0),
        ("deadline", 0.9), ("proposal", 1.0), ("review", 0.9), ("deliverable", 1.2),
        ("schedule", 1.0), ("office", 0.8), ("manager", 1.0), ("invoice", 0.9),
        ("follow-up", 0.8), ("action items", 1.0),
    ],
    "finance": [
        ("invoice", 1.3), ("payment", 1.3), ("bill", 1.2), ("refund", 1.2),
        ("transaction", 1.2), ("salary", 1.1), ("payroll", 1.2), ("bank", 1.0),
        ("amount due", 1.3), ("receipt", 1.0),
    ],
    "security": [
        ("password", 1.3), ("login", 1.2), ("security", 1.3), ("verify", 1.2),
        ("otp", 1.2), ("2fa", 1.2), ("suspicious", 1.1), ("account locked", 1.3),
        ("unauthorized", 1.3),
    ],
    "personal": [
        ("dinner", 1.3), ("family", 1.1), ("friend", 1.1), ("party", 1.1), ("weekend", 1.0),
        ("trip", 1.1), ("birthday", 1.3), ("let's", 0.9), ("catch up", 1.1), ("coffee", 1.0),
        ("home", 0.7), ("mom", 1.0), ("dad", 1.0),
    ],
}


STOPWORDS = {
    "the", "a", "an", "is", "are", "am", "to", "of", "and", "or", "for", "in", "on", "at",
    "by", "with", "this", "that", "it", "as", "we", "you", "your", "our", "be", "from", "please",
    "hi", "hello", "dear", "thanks", "thank", "regards",
}


TOPIC_PATTERNS = [
    (r"course|learning|academy|training|python|ideathon|faculty|university|college", "Course / Learning Invitation"),
    (r"invoice|payment|bill|refund", "Billing / Payment"),
    (r"discount|deal|coupon|sale|offer|shop|promo", "Promotional Offer"),
    (r"meeting|calendar|schedule|call", "Meeting / Schedule"),
    (r"project|milestone|delivery|report|proposal", "Project / Work Update"),
    (r"password|login|security|verify|otp|2fa", "Account Security"),
    (r"dinner|party|weekend|trip|birthday|family|friend", "Personal Plan"),
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9']+", text.lower())


def _extract_sender(text: str) -> str:
    for line in text.splitlines():
        if line.lower().startswith("from:"):
            return line.split(":", 1)[1].strip().lower()
    return ""


def _clean_subject(subject: str) -> str:
    cleaned = re.sub(r"^(re|fwd|fw)\s*:\s*", "", subject.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned[:120].strip() if cleaned else ""


def parse_email_text(raw_text: str) -> dict:
    text = raw_text.strip()
    subject = ""
    sender = _extract_sender(text)

    for line in text.splitlines():
        if line.lower().startswith("subject:"):
            subject = line.split(":", 1)[1].strip()
            break

    body = text
    if subject:
        body = re.sub(r"(?im)^subject:\s*.*$", "", text).strip()

    return {
        "subject": _clean_subject(subject),
        "sender": sender,
        "body": body,
        "full_text": f"{subject} {body}".strip(),
    }


def _apply_sender_heuristics(sender: str, scores: Counter) -> None:
    if not sender:
        return

    promotions_markers = ["newsletter", "promo", "offers", "marketing", "deals", "sale"]
    if any(marker in sender for marker in promotions_markers):
        scores["promotions"] += 1.0

    spam_markers = ["lottery", "winner", "claim-prize", "airdrop"]
    if any(marker in sender for marker in spam_markers):
        scores["spam"] += 1.3

    if "noreply" in sender or "no-reply" in sender:
        scores["promotions"] += 0.3

    personal_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    if any(sender.endswith(domain) for domain in personal_domains):
        scores["personal"] += 0.6

    work_markers = ["company.com", "corp", "inc", "team", "office", "manager", "support"]
    if any(marker in sender for marker in work_markers):
        scores["work"] += 0.7

    education_markers = ["edu", "university", "college", "academy", "school"]
    if any(marker in sender for marker in education_markers):
        scores["education"] += 0.8


def _apply_education_ham_heuristics(full_text: str, scores: Counter) -> bool:
    # Education invitations often contain words like "accept invitation" and "get started"
    # that look promotional but are legitimate in academic onboarding context.
    education_terms = [
        "course", "learning", "academy", "training", "python essentials", "ideathon",
        "faculty", "university", "college", "instructor", "my learning", "cisco",
    ]
    onboarding_terms = ["accept invitation", "get started", "setup or reset password"]

    edu_hits = sum(1 for term in education_terms if term in full_text)
    has_onboarding_phrase = any(term in full_text for term in onboarding_terms)

    if edu_hits >= 2 and has_onboarding_phrase:
        scores["education"] += 2.4
        scores["spam"] -= 1.1
        scores["work"] += 0.4
        return True

    if edu_hits >= 3:
        scores["education"] += 1.7
        scores["spam"] -= 0.6
        return True

    return False


def _score_sentences(sentences: list[str]) -> str:
    if not sentences:
        return "General Message"

    best_sentence = ""
    best_score = -1.0

    for sentence in sentences[:8]:
        norm = _normalize(sentence)
        tokens = _tokenize(norm)
        if len(tokens) < 4:
            continue

        score = 0.0
        for pattern, _topic in TOPIC_PATTERNS:
            if re.search(pattern, norm):
                score += 1.0

        if re.search(r"(need|required|submit|send|complete|review|confirm)", norm):
            score += 1.1
        if re.search(r"(today|tomorrow|eod|\d{1,2}:\d{2}|monday|tuesday|wednesday|thursday|friday)", norm):
            score += 0.9

        length_bonus = 0.5 if 8 <= len(tokens) <= 22 else 0.0
        score += length_bonus

        if score > best_score:
            best_score = score
            best_sentence = sentence.strip()

    if not best_sentence:
        best_sentence = sentences[0].strip()

    best_sentence = re.sub(r"^(hi|hello|dear)\b[\s,!:.-]*", "", best_sentence, flags=re.IGNORECASE).strip()
    best_sentence = re.sub(r"\s+", " ", best_sentence)
    words = [w for w in _tokenize(best_sentence) if w not in STOPWORDS]
    if not words:
        return "General Message"

    summary = " ".join(words[:10]).strip().capitalize()
    return summary[:100]


def detect_category(raw_text: str) -> tuple[str, float, str]:
    parsed = parse_email_text(raw_text)
    full_text = _normalize(parsed["full_text"])
    has_strong_urgency_term = bool(re.search(r"\b(urgent|asap|immediately|critical|action required)\b", full_text))
    scores = Counter({
        "education": 0.0,
        "promotions": 0.0,
        "spam": 0.0,
        "personal": 0.0,
        "urgent": 0.0,
        "work": 0.0,
        "finance": 0.0,
        "security": 0.0,
        "other": 0.0,
    })

    for category, keyword_pairs in CATEGORY_KEYWORDS.items():
        for keyword, weight in keyword_pairs:
            if keyword in full_text:
                scores[category] += weight

    _apply_sender_heuristics(parsed["sender"], scores)
    education_override = _apply_education_ham_heuristics(full_text, scores)

    # Mixed signal tuning: work + urgency should bias to urgent when response pressure is high.
    if scores["work"] >= 1.5 and scores["urgent"] >= 1.0:
        scores["urgent"] += 0.8
    if has_strong_urgency_term and scores["work"] >= 1.2:
        scores["urgent"] += 1.4
    if scores["security"] >= 1.5 and scores["urgent"] >= 0.8:
        scores["security"] += 0.8
    if scores["finance"] >= 1.5 and scores["spam"] >= 0.9 and "invoice" in full_text:
        scores["finance"] += 0.7
        scores["spam"] -= 0.4

    # Promotional language should map to promotions unless explicit scam markers dominate.
    if scores["promotions"] >= 1.3 and scores["spam"] >= 1.0:
        scores["promotions"] += 0.8
        scores["spam"] -= 0.5

    if any(term in full_text for term in ["lottery", "prize claim", "wire transfer", "bitcoin address"]):
        scores["spam"] += 1.2
        scores["promotions"] -= 0.2

    # Personal messages with promotional terms are often not true spam.
    if scores["personal"] >= 1.2 and scores["spam"] >= 1.0 and "unsubscribe" not in full_text:
        scores["personal"] += 0.5
        scores["spam"] -= 0.3

    top_category, top_score = scores.most_common(1)[0]
    second_score = scores.most_common(2)[1][1]

    if top_score <= 0:
        return "other", 0.45, "No strong category keywords found; defaulting to other."

    total_signal = max(sum(scores.values()), 1.0)
    dominance = max((top_score - second_score) / top_score, 0.0)
    evidence_strength = min(top_score / 4.0, 1.0)
    confidence = round(min(0.98, 0.5 + 0.3 * dominance + 0.2 * evidence_strength), 2)

    if top_category == "urgent" and scores["work"] >= 1.2:
        reason = "Detected mixed urgent + work signals; prioritized urgent due to time pressure terms."
    elif education_override and top_category in {"education", "work", "personal"}:
        reason = "Detected academic/course invitation context; reduced spam score and prioritized education." 
    elif top_category == "promotions" and scores["spam"] < max(1.8, scores["promotions"]):
        reason = "Detected marketing/promo intent without strong scam markers; classified as promotions."
    else:
        reason = f"Top weighted signals matched '{top_category}' (score {top_score:.1f})."

    return top_category, confidence, reason


def extract_main_subject(raw_text: str) -> str:
    parsed = parse_email_text(raw_text)
    subject = parsed["subject"]
    full_text = _normalize(parsed["full_text"])

    if subject:
        if len(subject) <= 70:
            return subject
        trimmed = re.sub(r"\s+", " ", subject)
        return (trimmed[:67].rstrip() + "...")

    for pattern, topic in TOPIC_PATTERNS:
        if re.search(pattern, full_text):
            return topic

    sentences = [s.strip() for s in re.split(r"[\n\.!?]+", parsed["body"]) if s.strip()]
    if not sentences:
        return "General Message"

    summary = _score_sentences(sentences)
    if summary and summary != "General Message":
        return summary

    first_sentence = re.sub(r"^(hi|hello|dear)\b[\s,!:.-]*", "", sentences[0], flags=re.IGNORECASE).strip()
    words = [w for w in _tokenize(first_sentence) if w not in STOPWORDS]
    if not words:
        return "General Message"
    return " ".join(words[:10]).capitalize()