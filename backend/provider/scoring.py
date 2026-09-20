
"""
Pure scoring functions. No DB, no request.

Question shape:
    {
        "id": "q1",
        "text": "...",
        "type": "single_choice" | "multiple_choice" | "boolean" | "likert" | "text",
        "options": [{"id": "a", "text": "..."}, ...],
        "correct": ["b"],        # ignored for psychometric
        "weight": 1,
        "trait": "conscientiousness"  # psychometric only
    }
"""
from typing import Any


def _normalize(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


def _score_question(question: dict, answer: Any) -> tuple[float, bool, str]:
    qtype = question.get("type", "single_choice")
    weight = float(question.get("weight", 1))

    if qtype == "likert":
        try:
            n = int(answer)
        except (TypeError, ValueError):
            return 0.0, False, "invalid_likert_value"
        if not (1 <= n <= 5):
            return 0.0, False, "likert_out_of_range"
        return weight, True, "recorded"

    if qtype == "text":
        return 0.0, False, "text_not_scored"

    correct = set(_normalize(question.get("correct")))
    given = set(_normalize(answer))

    if not correct:
        return 0.0, False, "no_correct_configured"

    if qtype == "multiple_choice":
        return (weight, True, "correct") if given == correct else (0.0, False, "incorrect")

    return (weight, True, "correct") if (len(given) == 1 and given == correct) else (0.0, False, "incorrect")


def score_attempt(assessment, answers: dict) -> dict:
    questions = assessment.questions or []
    total_weight = earned_weight = 0.0
    breakdown = []
    trait_buckets: dict[str, list[float]] = {}

    for q in questions:
        qid = str(q.get("id"))
        qtype = q.get("type", "single_choice")
        weight = float(q.get("weight", 1))
        answer = answers.get(qid)
        awarded, correct, reason = _score_question(q, answer)

        if assessment.kind == "psychometric" and qtype == "likert":
            trait = q.get("trait") or "general"
            try:
                trait_buckets.setdefault(trait, []).append(float(answer))
            except (TypeError, ValueError):
                pass

        if qtype in ("single_choice", "multiple_choice", "boolean"):
            total_weight += weight
            earned_weight += awarded

        breakdown.append({
            "question_id": qid, "type": qtype, "correct": correct,
            "awarded": awarded, "reason": reason,
        })

    if assessment.kind == "psychometric":
        score, passed = _score_psychometric(assessment, trait_buckets)
    else:
        score = round((earned_weight / total_weight) * 100, 2) if total_weight else 0.0
        passed = score >= assessment.pass_threshold

    return {
        "score": score,
        "passed": passed,
        "breakdown": breakdown,
        "trait_scores": {k: round(sum(v) / len(v), 3) for k, v in trait_buckets.items() if v},
    }


def _score_psychometric(assessment, trait_buckets) -> tuple[float, bool]:
    if not trait_buckets:
        return 0.0, False
    avgs = {t: sum(v) / len(v) for t, v in trait_buckets.items() if v}
    if not avgs:
        return 0.0, False
    overall = sum(avgs.values()) / len(avgs)
    score = round((overall / 5.0) * 100, 2)
    passed = all(a >= 3.0 for a in avgs.values()) and score >= assessment.pass_threshold
    return score, passed
