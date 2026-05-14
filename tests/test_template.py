"""Tests for crontab_gen.template module."""
import pytest

from crontab_gen.template import (
    TemplateEntry,
    delete_template,
    get_template,
    list_templates,
    save_template,
)


@pytest.fixture()
def tpl_file(tmp_path):
    return str(tmp_path / "templates.json")


class TestTemplateEntry:
    def test_to_dict_roundtrip(self):
        entry = TemplateEntry(name="daily", expression="0 0 * * *", description="midnight", tags=["prod"])
        restored = TemplateEntry.from_dict(entry.to_dict())
        assert restored.name == entry.name
        assert restored.expression == entry.expression
        assert restored.description == entry.description
        assert restored.tags == entry.tags

    def test_defaults(self):
        entry = TemplateEntry(name="x", expression="* * * * *")
        assert entry.description == ""
        assert entry.tags == []


class TestSaveTemplate:
    def test_save_and_retrieve(self, tpl_file):
        save_template("nightly", "0 2 * * *", path=tpl_file)
        entry = get_template("nightly", path=tpl_file)
        assert entry is not None
        assert entry.expression == "0 2 * * *"

    def test_overwrite_existing(self, tpl_file):
        save_template("job", "0 1 * * *", path=tpl_file)
        save_template("job", "0 5 * * *", path=tpl_file)
        entry = get_template("job", path=tpl_file)
        assert entry.expression == "0 5 * * *"

    def test_save_with_tags(self, tpl_file):
        save_template("tagged", "*/5 * * * *", tags=["monitoring", "prod"], path=tpl_file)
        entry = get_template("tagged", path=tpl_file)
        assert "monitoring" in entry.tags


class TestGetTemplate:
    def test_returns_none_for_missing(self, tpl_file):
        assert get_template("nonexistent", path=tpl_file) is None

    def test_returns_entry_for_existing(self, tpl_file):
        save_template("check", "*/10 * * * *", path=tpl_file)
        assert get_template("check", path=tpl_file) is not None


class TestListTemplates:
    def test_empty_when_no_templates(self, tpl_file):
        assert list_templates(path=tpl_file) == []

    def test_lists_all_saved(self, tpl_file):
        save_template("a", "* * * * *", path=tpl_file)
        save_template("b", "0 0 * * *", path=tpl_file)
        names = [e.name for e in list_templates(path=tpl_file)]
        assert "a" in names
        assert "b" in names


class TestDeleteTemplate:
    def test_delete_existing(self, tpl_file):
        save_template("to_del", "0 0 * * *", path=tpl_file)
        result = delete_template("to_del", path=tpl_file)
        assert result is True
        assert get_template("to_del", path=tpl_file) is None

    def test_delete_nonexistent_returns_false(self, tpl_file):
        assert delete_template("ghost", path=tpl_file) is False
