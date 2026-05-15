"""Integration tests for label feature: label + expression + explainer."""
import pytest

from crontab_gen.label import add_label, find_label, list_labels, remove_label
from crontab_gen.expression import is_valid
from crontab_gen.explainer import explain


@pytest.fixture
def label_file(tmp_path):
    return str(tmp_path / "labels.json")


SAMPLE = [
    ("* * * * *", "every minute"),
    ("0 * * * *", "every hour"),
    ("0 0 * * *", "daily at midnight"),
    ("0 0 * * 1", "every Monday"),
    ("*/5 * * * *", "every 5 minutes"),
]


class TestLabelIntegration:
    def test_all_labelled_expressions_are_valid(self, label_file):
        for expr, lbl in SAMPLE:
            add_label(expr, lbl, path=label_file)
        for entry in list_labels(path=label_file):
            assert is_valid(entry.expression), f"Invalid: {entry.expression}"

    def test_all_labelled_expressions_are_explainable(self, label_file):
        for expr, lbl in SAMPLE:
            add_label(expr, lbl, path=label_file)
        for entry in list_labels(path=label_file):
            result = explain(entry.expression)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_find_after_add(self, label_file):
        add_label("0 12 * * *", "noon daily", path=label_file)
        entry = find_label("0 12 * * *", path=label_file)
        assert entry is not None
        assert entry.label == "noon daily"

    def test_remove_reduces_count(self, label_file):
        for expr, lbl in SAMPLE:
            add_label(expr, lbl, path=label_file)
        before = len(list_labels(path=label_file))
        remove_label(SAMPLE[0][0], path=label_file)
        after = len(list_labels(path=label_file))
        assert after == before - 1

    def test_label_preserved_after_reload(self, label_file):
        add_label("30 6 * * 1-5", "weekday mornings", path=label_file)
        entry = find_label("30 6 * * 1-5", path=label_file)
        assert entry is not None
        assert entry.label == "weekday mornings"
        assert is_valid(entry.expression)
