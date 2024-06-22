import pytest
from PIL import PdfParser

def test_delitem_new_entries():
    parser = PdfParser.XrefTable()
    parser.new_entries["test_key"] = ("value", 0)

    del parser["test_key"]

    assert "test_key" not in parser.new_entries
    assert parser.deleted_entries["test_key"] == 1


def test_delitem_deleted_entries():
    parser = PdfParser.XrefTable()
    parser.deleted_entries["test_key"] = 0

    del parser["test_key"]

    assert parser.deleted_entries["test_key"] == 0

def test_delitem_nonexistent_key():
    parser = PdfParser.XrefTable()

    with pytest.raises(IndexError):
        del parser["nonexistent_key"]