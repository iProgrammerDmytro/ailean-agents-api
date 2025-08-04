from difflib import SequenceMatcher
from typing import Final

_QA_PAIRS: Final[dict[str, str]] = {
    "check-in": "Check-in starts at 16:00 (4 PM) and is open until late.",
    "check-out": "Check-out is by 11:00 AM.",
    "parking": "Self-parking is available for CHF 25 per day.",
    "breakfast": "A continental buffet breakfast is included and free.",
    "pets": "Pets are allowed (1 dog max) with a CHF 50 per stay fee.",
    "coffee": (
        "Help yourself at our self-service coffee bar at any time of the day - "
        "just pick your favourite pod and brew away."
    ),
    "digital concierge": (
        "An AI-powered digital concierge is available 24/7 via chat whenever you need help."
    ),
    "services": (
        "Need extra cleaning or more towels? You can add bookable services straight "
        "from your smartphone."
    ),
    "work hub": (
        "Absolutely, we have a stylish work hub, making The Grand Arosa the perfect workation spot."
    ),
    "long stay": (
        "Looking for an extended break? Long-stay guests can live here from CHF 990 per month "
        "when they book 30-day packages (summer offer)."
    ),
    "location": "We're at 269 Poststrasse, 7050 Arosa, in the canton of Grisons.",
}

_FALLBACK = "Sorry, I couldn't find an answer to that."
_MIN_FUZZ_RATIO: Final[float] = 0.56


def _norm(s: str) -> str:
    """
    Lower-case + strip all non-alphanumeric chars.

    Example:
        "Check-in"  -> "checkin"
        "PARKING!!" -> "parking"
    """
    return "".join(ch for ch in s.lower() if ch.isalnum())


def _ratio(a: str, b: str) -> float:
    """Cheap fuzzy similarity."""
    return SequenceMatcher(None, a, b).ratio()


def answer(question: str) -> str:
    q_norm = _norm(question)

    # 1️⃣ exact / substring pass on normalised forms
    for k, v in _QA_PAIRS.items():
        k_norm = _norm(k)
        if k_norm in q_norm or q_norm in k_norm:
            return v

    # 2️⃣ fuzzy pass on normalised forms (handles typos like 'cheeckin')
    best_key = max(_QA_PAIRS, key=lambda k: _ratio(q_norm, _norm(k)))
    if _ratio(q_norm, _norm(best_key)) >= _MIN_FUZZ_RATIO:
        return _QA_PAIRS[best_key]

    return _FALLBACK
