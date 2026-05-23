"""Tests for crontab_gen.symmetry."""
import pytest

from crontab_gen.symmetry import SymmetryResult, analyse_symmetry


class TestSymmetryResult:
    def _make(self, score=0.0, pairs=None):
        return SymmetryResult(
            expression_a="0 6 * * *",
            expression_b="0 18 * * *",
            mirrored_pairs=pairs or [],
            score=score,
        )

    def test_str_contains_expressions(self):
        r = self._make()
        assert "0 6 * * *" in str(r)
        assert "0 18 * * *" in str(r)

    def test_str_contains_score(self):
        r = self._make(score=0.75)
        assert "0.75" in str(r)

    def test_str_contains_symmetric_label_when_high_score(self):
        r = self._make(score=1.0)
        assert "symmetric" in str(r)

    def test_str_contains_asymmetric_label_when_low_score(self):
        r = self._make(score=0.2)
        assert "asymmetric" in str(r)

    def test_is_symmetric_true_at_threshold(self):
        r = self._make(score=0.5)
        assert r.is_symmetric is True

    def test_is_symmetric_false_below_threshold(self):
        r = self._make(score=0.49)
        assert r.is_symmetric is False

    def test_str_contains_paired_count(self):
        r = self._make(score=0.0, pairs=[])
        assert "0" in str(r)


class TestAnalyseSymmetry:
    def test_invalid_expression_a_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            analyse_symmetry("not valid", "0 6 * * *")

    def test_invalid_expression_b_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            analyse_symmetry("0 6 * * *", "bad expr")

    def test_returns_symmetry_result(self):
        result = analyse_symmetry("0 6 * * *", "0 18 * * *")
        assert isinstance(result, SymmetryResult)

    def test_perfectly_mirrored_has_high_score(self):
        # 06:00 and 18:00 are mirrors (6*60=360, 18*60=1080, 360+1080=1440)
        result = analyse_symmetry("0 6 * * *", "0 18 * * *")
        assert result.score >= 0.5

    def test_identical_expressions_score_is_one(self):
        # midnight mirrors itself (0 + 1440 - 0 = 1440 => mirror is 0)
        result = analyse_symmetry("0 0 * * *", "0 0 * * *")
        assert result.score == 1.0

    def test_unrelated_expressions_have_low_score(self):
        result = analyse_symmetry("0 1 * * *", "0 7 * * *")
        assert result.score < 0.5

    def test_expression_attributes_preserved(self):
        result = analyse_symmetry("0 6 * * *", "0 18 * * *")
        assert result.expression_a == "0 6 * * *"
        assert result.expression_b == "0 18 * * *"

    def test_mirrored_pairs_are_tuples(self):
        result = analyse_symmetry("0 6 * * *", "0 18 * * *")
        for pair in result.mirrored_pairs:
            assert isinstance(pair, tuple)
            assert len(pair) == 2

    def test_tolerance_widens_matching(self):
        # 06:00 vs 18:01 — not exact mirror, but within 1-minute tolerance
        strict = analyse_symmetry("0 6 * * *", "1 18 * * *", tolerance_minutes=0)
        lenient = analyse_symmetry("0 6 * * *", "1 18 * * *", tolerance_minutes=1)
        assert lenient.score >= strict.score
