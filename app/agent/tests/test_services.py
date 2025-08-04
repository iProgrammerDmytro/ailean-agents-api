import pytest
from pytest import MonkeyPatch

from app.agent.services.qa import _FALLBACK, _QA_PAIRS, _norm, answer


class TestAnswerFunction:
    """Unit-level validations for answer(question)."""

    @pytest.mark.parametrize(
        "question,expected_key",
        [
            ("What time is check-in?", "check-in"),
            ("When do we check-out ?", "check-out"),
            ("Is there PARKING on site", "parking"),
            ("Is BREAKFAST included?", "breakfast"),
            ("Are pets allowed in rooms?", "pets"),
            ("What is your location?", "location"),
            ("Do you have a coffee bar?", "coffee"),
            ("Can I book extra SERVICES?", "services"),
            ("Is there a WORK HUB for laptops?", "work hub"),
            ("Can I stay for a MONTH-LONG STAY deal?", "long stay"),
        ],
    )
    def test_exact_substring_match_hits(self, question: str, expected_key: str) -> None:
        assert answer(question) == _QA_PAIRS[expected_key]

    @pytest.mark.parametrize(
        "question,expected_key,typo",
        [
            ("cheeckin time please", "check-in", "cheeckin"),  # extra 'e'
            ("parkin price?", "parking", "parkin"),  # dropped 'g'
            ("brkfast options?", "breakfast", "brkfast"),  # missing vowels
        ],
    )
    def test_fuzzy_match_hits(
        self, question: str, expected_key: str, typo: str
    ) -> None:
        output = answer(question)
        assert (
            output == _QA_PAIRS[expected_key]
        ), f"expected typo '{typo}' to map to {expected_key}"

    @pytest.mark.parametrize(
        "question",
        [
            "Do you have a spa?",
            "Is there ski rental on site?",
            "How many stars is the hotel?",
        ],
    )
    def test_fallback_when_no_match(self, question: str) -> None:
        assert answer(question) == _FALLBACK

    def test_norm_helper(self) -> None:
        """_norm should drop punctuation and lowercase."""
        assert _norm("Check-In!!!") == "checkin"

    def test_ratio_threshold_is_respected(self, monkeypatch: MonkeyPatch) -> None:
        """If we crank the threshold above any match, we should fall back."""
        monkeypatch.setattr(
            "app.agent.services.qa._MIN_FUZZ_RATIO", 0.99
        )  # impossible bar
        assert answer("cheeckin time?") == _FALLBACK
